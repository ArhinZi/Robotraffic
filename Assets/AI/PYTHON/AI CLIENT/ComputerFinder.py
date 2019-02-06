import cv2
import numpy as np

class ComputerFinder:
    original = None
    gray = None
    res = None

    def __init__(self, img):
        self.original = img
        if(img is not None):
            self.gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    def show(self, name, img):
        if(img is not None):
            cv2.imshow(name, img)
            cv2.waitKey(1)

    def threshold(self, img, C = 201, dst = 5):
        th2 = None
        if(img is not None):
            th2 = cv2.adaptiveThreshold (img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, C, dst)
        return th2

    def findPath(self, timg, threshold = 0.7, size = 512, w = 50, h = 21):
        whs = 0
        th2 = None
        start_w = None
        width = None
        mass = [ [ 0 for y in range( 2 ) ] for x in range( 2 ) ]
        if(timg is not None):
            for j in range(0,size):
                if(start_w is None):
                    hs = 0
                    for i in range(size-h, size):
                        if(timg[i,j] == 0):
                            hs+=1

                    if(hs/h > threshold):
                        start_w = j
                        width = 1
                
                else:
                    hs = 0
                    for i in range(size-h, size):
                        if(timg[i,j] == 0):
                            hs+=1
                    if(hs/h > threshold):
                        width += 1
                    else:
                        mass[0][0] = start_w
                        mass[0][1] = width
                        start_w = None

            tl = (mass[0][0], 512 - 20)
            br = (mass[0][0]+mass[0][1], 512)
            cv2.rectangle(timg, tl, br, (100), thickness=1, lineType=8, shift=0)
        else:
            return None

        return timg;