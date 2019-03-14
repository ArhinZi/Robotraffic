import cv2
import numpy as np


class Node:
    coords = [0, 0]
    parent = None
    childs = []
    line = None
    c_w = 0
    level = 0

    def __init__(self, coords, line):
        self.coords = coords
        self.line = line

class ComputerFinder:
    debug = False
    original = None
    color_img = None
    gray_img = None
    res = None
    size = None
    mult = None

    def __init__(self, img, target_size=128):
        if(img is not None):
            self.original = cv2.resize(img, (512, 512))
            self.color_img = cv2.resize(img, (target_size, target_size))
            self.gray_img = cv2.cvtColor(self.color_img, cv2.COLOR_BGR2GRAY)
            self.size = target_size
            self.mult = int(512/self.size)

    #Show image in CV2 window
    def show(self, name, img):
        if(img is not None):
            cv2.imshow(name, img)
            k = cv2.waitKey(1) & 0xFF
            if k == 27:
                return False
        return True

    #Adaptive binary threshold
    def threshold(self, img, C=201, dst=5):
        th2 = None
        if(img is not None):
            th2 = cv2.adaptiveThreshold(
                img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, C, dst)
        return th2

    def drawTree(self, img, tree, n, m, h):
        for i in reversed(range(m)):
            for j in range(n):
                if(tree[i][j] is not None):
                    tl = (tree[i][j].coords[0]*self.mult, (self.size - tree[i][j].line - int(h/2))*self.mult-2)
                    br = (tree[i][j].coords[1]*self.mult, (self.size - tree[i][j].line - int(h/2))*self.mult)
                    cv2.rectangle(img, tl, br, (0,0,255), thickness=2, lineType=8, shift=0)

                    if(tree[i][j].parent is not None):
                        parent = tree[i][j].parent
                        p = (tree[parent[0]][parent[1]].coords[0]*self.mult, (self.size - tree[parent[0]][parent[1]].line - int(h/2))*self.mult-2)
                        cv2.line(img,br,p,(255,0,0), thickness=2, lineType=8, shift=0)


    def reverseDrawPath(self, img, tree, node, h, segment_color, line_color):
        if(node is not None):
            tl = (node.coords[0]*self.mult, (self.size - node.line - int(h/2))*self.mult-2)
            br = (node.coords[1]*self.mult, (self.size - node.line - int(h/2))*self.mult)
            cv2.rectangle(img, tl, br, segment_color, thickness=2, lineType=8, shift=0)
            if(node.parent is not None):
                    parent = tree[node.parent[0]][node.parent[1]]
                    p = (parent.coords[0]*self.mult, (self.size - parent.line - int(h/2))*self.mult-2)
                    cv2.line(img,br,p,line_color, thickness=2, lineType=8, shift=0)
                    self.reverseDrawPath(img, tree, parent, h, segment_color, line_color)


            return 0;

            

    def findPath(self, timg, flatten_threshold, perspective_k, vision_k, min_w, max_w, h, step):
        if(timg is not None):
            n = int(self.size/min_w)
            m = int(self.size/h)
            tree = [[None]*n]*m
            tree = np.array(tree)
            tree[0][0] = Node([0,self.size], 0)

            #foreach in discrete lines with the set height in image
            for l in range(0, int(self.size*vision_k/h), step):

            #flattening the line to 1 pixel
                
                line_array = np.zeros(self.size)    

                #foreach in pixels in line
                for i in range(0, self.size):

                    #height of black part of line by height
                    hs = 0 
                    
                    #foreach in pixels by height in the line
                    for j in range(self.size-h*(l+1), self.size - h*l):
                        if(timg[j, i] == 0):
                            hs += 1
                    
                    if(hs/h >= flatten_threshold):
                        line_array[i] = 1
                    else:
                        line_array[i] = 0

            #creating potential childs
                
                potential_childs = []

                start_x = None
                width = None
                for i in range(len(line_array)):
                    if(line_array[i] == 1):
                        if(start_x is None):
                            start_x = i
                            width = 0
                        else:
                            width += 1

                    if(line_array[i] == 0 or i==len(line_array)-1):
                        if(start_x is None):
                            pass
                        else:
                            node = Node([start_x,start_x+width], l*h + (int(self.size/h)%step))
                            potential_childs.append(node)
                            start_x = None
                            width = None

                

            #finding right childs

                for child in potential_childs:
                    b_flag = False
                    for i in reversed(range(m)):
                        for j in range(n):
                            if(
                                tree[i][j] is not None and
                                min_w < child.coords[1]-child.coords[0] and
                                tree[i][j].coords[0] < ((child.coords[0]+child.coords[1])/2) < tree[i][j].coords[1] and
                                tree[i][j].coords[1]-tree[i][j].coords[0] >= child.coords[1]-child.coords[0] and
                                tree[i][j].line <= child.line
                                ):

                                child_i = i+1
                                child_j = 0
                                for pos in range(n):
                                    if(tree[i+1][pos] is None):
                                        child_j = pos
                                        break

                                child.parent = [i,j]
                                child.c_w = (tree[i][j].c_w + (child.coords[1]+child.coords[0]))/2 - self.size/2
                                child.level = tree[i][j].level+1
                                tree[child_i][child_j] = child

                                tree[i][j].childs.append([child_i, child_j])
                                tree[child_i][child_j].childs = []

                                b_flag = True
                                break
                        if(b_flag):
                            break


            #finding true path

            tree[0][0].c_w = self.size
            max_i = self.size
            true_last_node = None
            for i in reversed(range(m)):
                b = False
                for j in range(n):
                    if(
                       tree[i][j] is not None and 
                       abs(tree[i][j].c_w) < max_i and 
                       tree[i][j].childs == [] and 
                       tree[i][j].level > 6 and
                       tree[i][j].coords[1]-tree[i][j].coords[0] < max_w
                       ):

                        max_i = abs(tree[i][j].c_w)
                        true_last_node = tree[i][j]
                        b = True
                        break
                if(b):
                    break


            #finding stop segments of tree
            true_stop_node = None
            for i in reversed(range(m)):
                b = False
                for j in range(n):
                    if(
                       true_last_node is not None and 
                       tree[i][j] is not None and
                       tree[i][j].parent is not None and
                       (tree[i][j].coords[0]+tree[i][j].coords[1])/2>(true_last_node.c_w+self.size/2)>tree[i][j].coords[0] and 
                       self.size/1.5>(tree[i][j].coords[1]-tree[i][j].coords[0])>max_w
                       ):

                        true_stop_node = tree[i][j]
                        b = True
                        break
                if(b):
                    break

            img = self.original.copy()
            self.drawTree(img, tree, n, m, h)
            self.show("tree",img)

            return (tree, true_last_node, true_stop_node);


    def drawPoints(self, img, coords):
        if(img is not None):
            for k in coords:
                cv2.circle(img, (k[0]*self.mult, k[1]*self.mult), 2, (0, 0, 100), 1)
                cv2.circle(img, (k[0]*self.mult, k[1]*self.mult), 5, (0, 100, 0), 1)
        return img
