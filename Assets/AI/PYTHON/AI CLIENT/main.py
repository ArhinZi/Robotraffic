import io
import json as json_
import math
import socket
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
    arr = np.array(Image.open(imageStream))
    try:
        open_cv_image = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
    except:
        return None
    return open_cv_image




class RealtimePlot:
    def __init__(self, axes, max_entries=1000):
        self.axis_x = deque(maxlen=max_entries)
        self.axis_y = deque(maxlen=max_entries)
        self.axes = axes
        self.max_entries = max_entries

        self.lineplot, = axes.plot([], [], "ro-")
        self.axes.set_autoscaley_on(True)

    def add(self, x, y):
        self.axis_x.append(x)
        self.axis_y.append(y)
        self.lineplot.set_data(self.axis_x, self.axis_y)
        self.axes.set_xlim(self.axis_x[0], self.axis_x[-1] + 1e-15)
        self.axes.relim()
        self.axes.autoscale_view()  # rescale the y-axis

    def animate(self, figure, callback, interval=50):
        import matplotlib.animation as animation

        def wrapper(frame_index):
            self.add(*callback(frame_index))
            self.axes.relim()
            self.axes.autoscale_view()  # rescale the y-axis
            return self.lineplot
        animation.FuncAnimation(figure, wrapper, interval=interval)

def ConnectBySocket(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    return s

def nothing(x):
    pass

start = time_.time()



if __name__ == "__main__":
    
    fig, axes = plt.subplots()
    display = RealtimePlot(axes)

    s = ConnectBySocket('localhost', 9090)
    
    last_time = 0

    cv2.namedWindow("Main", cv2.WINDOW_NORMAL)
    cv2.createTrackbar('k1','Main',0,24,nothing)
    flag = True
    while flag:
        last_time = millis()
        s.send('Request Data'.encode("utf-8"))
        data = s.recv(1000000)

        image = png_bytes_2_opencv_image(data)
        
        cf = ComputerFinder(image)

        coords = cf.findPath(cf.threshold(cf.gray))
        flag = cf.show("Main", cf.drawPoints(image, coords))

        timer = millis()-last_time
        # print(timer)

        data = s.recv(1000000)
        try:
            decoded_data = data.decode("utf-8")
            json = json_.loads(decoded_data)
            display.add(time_.time() - start,
                        float(json['CurrentSteering'].replace(",", ".")))
            plt.pause(0.0001)
        except Exception as e:
            print(e)
        
        # input()

    s.close()
