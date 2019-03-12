import cv2
import numpy as np


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

    def findPath(self, timg, threshold=0.7, perspective_k = 0.94, next_max_width_k = 1.1, next_max_center_k = 0.4, min_w=5, max_w=50, h=2, step=2):
        if(timg is not None):
            mass = [{"coords": [0, 0], "widths": [0, 0]}
                for x in range(int(self.size/h))]


            #foreach in discrete lines in image with the set height
            for l in range(0, int(self.size/h), step):
                width = None #current line width
                start_w = None #line start
                b_flag = False 

                #foreach in pixels in line
                for j in range(0, self.size):
                    hs = 0
                    

                    #foreach in pixels by height in the line
                    for i in range(self.size-h*(l+1), self.size - h*l):
                        if(timg[i, j] == 0):
                            hs += 1

                    if(start_w is None):
                        if(hs/h > threshold):
                            start_w = j
                            width = 1

                    else:
                        if(hs/h > threshold and (not b_flag)):
                            width += 1

                        else:
                            if(max_w > width > min_w and start_w != 0):
                                if((l-step > 0 and width > mass[l-step]["widths"][1]*next_max_width_k and mass[l-step]["widths"][1] > 10)):
                                    break

                                flag = False #flag for save
                                if(
                                    (l-step >= 0 and (mass[l-step]["widths"][0]+width*next_max_center_k < int(start_w + width/2) < mass[l-step]["widths"][0]+mass[l-step]["widths"][1]-width*next_max_center_k)) or
                                    l == 0
                                ):

                                    flag = True

                                elif((mass[l-step]["coords"][0] == 0)):
                                    not_none_exist = False
                                    for m in range(l-step, 0, -1*step):
                                        if(mass[m]["coords"][0] != 0):
                                            not_none_exist = True
                                            if(mass[m]["widths"][0]+width*next_max_center_k/2 < int(start_w + width/2) < mass[m]["widths"][0]+mass[m]["widths"][1]-width*next_max_center_k/2):
                                                flag = True
                                                break
                                            else:
                                                break
                                    if(not not_none_exist):
                                        flag = True


                                if(flag):
                                    mass[l]["coords"] = [
                                        int(start_w + width/2), int(self.size - h*l - h/2)]
                                    mass[l]["widths"] = [
                                        int(start_w), int(width)]
                                    break
                            else:
                                pass
                            start_w += width
                            width = 1         
            if(self.debug):
                d_img = self.original.copy()
                for k in range(int(self.size/h)):
                    tl = (mass[k]["widths"][0]*self.mult, (self.size - h*(k+1))*self.mult)
                    br = ((mass[k]["widths"][0]+mass[k]["widths"][1])*self.mult, (self.size - h*k)*self.mult)
                    cv2.rectangle(d_img, tl, br, (0,0,255), thickness=1, lineType=8, shift=0)
                self.show("FindPath", d_img)
        else:
            return None

        coords0 = list(map(lambda x: x["coords"], mass))
        coords = []
        for i in coords0:
            if(i[0] != 0):
                coords.append(i)
        return coords

    def drawPoints(self, img, coords):
        if(img is not None):
            for k in coords:
                cv2.circle(img, (k[0]*self.mult, k[1]*self.mult), 2, (0, 0, 100), 1)
                cv2.circle(img, (k[0]*self.mult, k[1]*self.mult), 5, (0, 100, 0), 1)
        return img
