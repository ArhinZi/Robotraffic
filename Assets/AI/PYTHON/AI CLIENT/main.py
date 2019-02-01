import socket
import sys
import time as time_
import io
from PIL import Image
import cv2
import numpy as np
from matplotlib import pyplot as plt


def millis():
    return int(round(time_.time() * 1000))

def show_png(png_bytes):
    imageStream = io.BytesIO(png_bytes)
    arr = np.array(Image.open(imageStream))
    if(arr is not None):
        open_cv_image = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR) 
        cv2.imshow("img", open_cv_image)
        cv2.waitKey(1)

import math
from collections import deque

start = time_.time()

class RealtimePlot:
    def __init__(self, axes, max_entries = 100):
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
        self.axes.relim(); self.axes.autoscale_view() # rescale the y-axis

    def animate(self, figure, callback, interval = 50):
        import matplotlib.animation as animation
        def wrapper(frame_index):
            self.add(*callback(frame_index))
            self.axes.relim(); self.axes.autoscale_view() # rescale the y-axis
            return self.lineplot
        animation.FuncAnimation(figure, wrapper, interval=interval)

        


if __name__ == "__main__": 
    fig, axes = plt.subplots()
    display = RealtimePlot(axes)
    display.animate(fig, lambda frame_index: (time_.time() - start, 25))
    plt.show()

    fig, axes = plt.subplots()
    display = RealtimePlot(axes)


    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = 'localhost'
    port = 9090
    s.connect((host, port))
    last_time = 0
    while True:
        time_.sleep(0.01)
        # print("Sending")
        # last_time = millis()
        s.send('Request Data'.encode("utf-8"))
        data = s.recv(1000000)
        # timer = millis()-last_time
        show_png(data)
        # print('Received:', len(data), 'bytes', "Time:", timer)

        display.add(time_.time() - start, 23)
        plt.pause(0.001)
    s.close()