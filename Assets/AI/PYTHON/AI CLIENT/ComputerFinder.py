import cv2
import numpy as np


class ComputerFinder:
    original = None
    gray = None
    res = None

    def __init__(self, img, target_size=128):
        print(111)
        if(img is not None):
            self.original = cv2.resize(img, (target_size, target_size))
            self.gray = cv2.cvtColor(self.original, cv2.COLOR_BGR2GRAY)

    def show(self, name, img):
        if(img is not None):
            cv2.imshow(name, img)
            k = cv2.waitKey(1) & 0xFF
            if k == 27:
                return False
        return True

    def threshold(self, img, C=201, dst=5):
        th2 = None
        if(img is not None):
            th2 = cv2.adaptiveThreshold(
                img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, C, dst)
        return th2

    def findPath(self, timg, threshold=0.7, size=128, min_w=5, max_w=50, h=2, step=2):
        mass = [{"coords": [0, 0], "widths": [0, 0]}
                for x in range(int(size/h))]
        if(timg is not None):
            for l in range(0, int(size/h), step):
                width = None
                start_w = None
                b_flag = False

                for j in range(0, size):
                    hs = 0
                    for i in range(size-h*(l+1), size - h*l):
                        if(timg[i, j] == 0):
                            hs += 1

                    if(start_w is None):
                        if(hs/h > threshold):
                            start_w = j
                            width = 1

                    else:
                        if(hs/h > threshold and (not b_flag)):
                            width += 1

                            if(
                                l-step > 0 and
                                width >= mass[l-step]["widths"][1] and
                                (mass[l-step]["widths"][0] < int(start_w + width/2) <
                                 mass[l-step]["widths"][0]+mass[l-step]["widths"][1])
                            ):
                                b_flag = True

                        else:
                            if(width > min_w and width < max_w):
                                flag = False
                                if(
                                    (l-step >= 0 and (mass[l-step]["widths"][0] < int(start_w + width/2) < mass[l-step]["widths"][0]+mass[l-step]["widths"][1])) or
                                    b_flag or
                                    l == 0
                                ):
                                    flag = True

                                elif((mass[l-step]["coords"][0] == 0)):
                                    for m in range(l-step, 0, -1*step):
                                        if(mass[m]["coords"][0] != 0):
                                            if(mass[m]["widths"][0] < int(start_w + width/2) <
                                               mass[m]["widths"][0]+mass[m]["widths"][1]):
                                                flag = True
                                                break
                                            else:
                                                break

                                if(flag):
                                    mass[l]["coords"] = [
                                        int(start_w + width/2), int(size - h*l - h/2)]
                                    mass[l]["widths"] = [
                                        int(start_w), int(width)]
                                    break

                            else:
                                pass
                            start_w += width
                            width = 1
                            b_flag = False

            # for k in range(int(size/h)):
            #     tl = (mass[k]["widths"][0], size - h*(k+1))
            #     br = (mass[k]["widths"][0]+mass[k]["widths"][1], size - h*k)

            #     cv2.rectangle(timg, tl, br, (100),
            #                   thickness=1, lineType=8, shift=0)
            # self.show("r", timg)
        else:
            return None

        coords0 = list(map(lambda x: x["coords"], mass))
        coords = []
        for i in coords0:
            if(i[0] != 0):
                coords.append(i)
        return coords

    def drawPoints(self, img, coords, mult=4):
        if(img is not None):
            for k in coords:
                cv2.circle(img, (k[0]*mult, k[1]*mult), 2, (0, 0, 100), 1)
                cv2.circle(img, (k[0]*mult, k[1]*mult), 5, (0, 100, 0), 2)
        return img
