#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io
import PIL
import json as json_
import math
import socket
import threading
import sys
import time as time_
import cv2
import numpy as np

import ComputerFinder

from pprint import pprint
from matplotlib import pyplot as plt
from PIL import Image


def millis():
    return int(round(time_.time() * 1000))


def png_bytes_2_opencv_image(png_bytes):
    imageStream = io.BytesIO(png_bytes)
    try:
        arr = np.array(Image.open(imageStream))
        open_cv_image = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
    except:
        return None
    return open_cv_image


def ConnectBySocket(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    return s


def nothing(x):
    pass

def main():
    s = ConnectBySocket('localhost', 9090)
    flag = True
    ls = 0
    while flag:
        
        # Request for photo
        s.send('Request Data'.encode("utf-8"))

        # Recieve photo
        data = s.recv(1000000)

        #last_time = millis()
        image = png_bytes_2_opencv_image(data)
        cf = ComputerFinder.ComputerFinder(image,64)
        cf.debug = True
        last_time = millis()
        h = 4
        (tree,node) = cf.findPath(cf.threshold(cf.gray_img), flatten_threshold=0.7, perspective_k = 0.94, vision_k=0.7, min_w=2, max_w=20, h=h, step=1)
        
        find_timer = millis()-last_time

        # Recieve state
        data = s.recv(1000000)
        state = {}
        try:
            decoded_data = data.decode("utf-8")
            state = json_.loads(decoded_data)
        except Exception as e:
            print(e,"78")

        # Send control commands
        target_steering = 0
        if(node is not None):
            target_steering = node.c_w
        if(ls is not None):
            for z in range(2):
                target_steering = (ls+target_steering)/2
                target_steering = int(target_steering*1.4)
        sdict = {
            "speed": 15,
            "steering": int(target_steering)
        }
        json = json_.dumps(sdict, sort_keys=True)
        s.send(json.encode("utf-8"))

        # Recieve response
        data = s.recv(1000000)
        try:
            decoded_data = data.decode("utf-8")
            #print(decoded_data)
        except Exception as e:
            print(e)
        

        cv2.putText(cf.original,'speed:'+state["CurrentSpeed"],(0,20), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1,(0,0,0),1,cv2.LINE_AA)
        cv2.putText(cf.original,'steering:'+state["CurrentSteering"],(0,40), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1,(0,0,0),1,cv2.LINE_AA)
        cv2.putText(cf.original,'ms:'+str(find_timer),(0,60), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1,(0,0,0),1,cv2.LINE_AA)
        cf.reverseDrawPath(cf.original, tree, node, h)
        flag = cf.show("Main", cf.original)

        # input()

    s.close()



if __name__ == "__main__":
    t = threading.Thread(target=main)
    t.daemon = False
    t.start()