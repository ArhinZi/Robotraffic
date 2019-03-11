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
from collections import deque
from pprint import pprint

import cv2
import numpy as np
from matplotlib import pyplot as plt
from PIL import Image

from ComputerFinder import ComputerFinder


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

def main(show_window = False):
    s = ConnectBySocket('localhost', 9090)
    start = time_.time()
    if(show_window):
        cv2.namedWindow("Main", cv2.WINDOW_NORMAL)
        cv2.createTrackbar('speed', 'Main', 0, 15, nothing)
    flag = True
    last_ts = None
    while flag:
        

        # Request for photo
        s.send('Request Data'.encode("utf-8"))

        # Recieve photo
        data = s.recv(1000000)

        #last_time = millis()
        image = png_bytes_2_opencv_image(data)
        cf = ComputerFinder(image,128)
        cf.debug = True
        #last_time2 = millis()
        coords = cf.findPath(cf.threshold(cf.gray_img), 0.7, 0.94, 1.3, 0.4, 5, 40, 2, 2)

        # Recieve state
        data = s.recv(1000000)
        state = {}
        try:
            decoded_data = data.decode("utf-8")
            state = json_.loads(decoded_data)
        except Exception as e:
            print(e,"78")

        # Calculate commands
        target_steering = 0
        k = 0
        if( coords is not None):
            for i in coords[:int(len(coords)/2)]:
                target_steering += i[0]
                k += 1
        
            if(k != 0):
                target_steering = int(target_steering/k)-64
                if(last_ts is not None):
                    for z in range(2):
                        target_steering = (last_ts+target_steering)/2
                    target_steering = int(target_steering*0.8)
        target_speed = cv2.getTrackbarPos('speed', 'Main')

        # Send control commands
        sdict = {
            "speed": target_speed,
            "steering": target_steering
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

        if(show_window):
            img = cf.drawPoints(image, coords)
            if(state != {}):
                cv2.putText(img,'speed:'+state["CurrentSpeed"],(0,20), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1,(0,0,0),1,cv2.LINE_AA)
                cv2.putText(img,'steering:'+state["CurrentSteering"],(0,40), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1,(0,0,0),1,cv2.LINE_AA)

            flag = cf.show("Main", img)
        # input()
        last_ts = target_steering

    s.close()

def main2():
    s = ConnectBySocket('localhost', 9090)
    start = time_.time()
    flag = True
    while flag:
        

        # Request for photo
        s.send('Request Data'.encode("utf-8"))

        # Recieve photo
        data = s.recv(1000000)

        #last_time = millis()
        image = png_bytes_2_opencv_image(data)
        cf = ComputerFinder(image,128)
        cf.debug = True
        #last_time2 = millis()
        coords = cf.findPath2(cf.threshold(cf.gray_img), flatten_threshold=0.7, perspective_k = 0.94, min_w=5, max_w=50, h=2, step=2)

        # Recieve state
        data = s.recv(1000000)
        state = {}
        try:
            decoded_data = data.decode("utf-8")
            state = json_.loads(decoded_data)
        except Exception as e:
            print(e,"78")

        # Send control commands
        sdict = {
            "speed": 5,
            "steering": 0
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
        
        flag = cf.show("Main", cf.original)
        # input()

    s.close()



if __name__ == "__main__":
    #t = threading.Thread(target=main, args=(True,))
    #t.daemon = False
    #t.start()
    main2()