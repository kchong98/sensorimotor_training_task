import tkinter as tk
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from threading import Thread, Event
import serial
import numpy as np
from time import sleep
import sys


class gui:
    def __init__(self, root):
        super().__init__()
        self.root = root
        self.data = np.array([0,0,0,0])
        self.saved_data = np.empty(shape = (4))
        self.stop_data = Event()
        self.var1 = tk.IntVar()
        self.slide_val = tk.DoubleVar()
        self.slide_val.set(1.5)
        c1 = tk.Checkbutton(self.root, text='Generate Data', variable=self.var1, onvalue=1, offvalue=0)
        c1.grid(row = 1, column=1, columnspan=3)

        self.fig = plt.figure(figsize = (8,8))
        self.ax = self.fig.add_axes([0,0.05,1,0.95])
        self.plot()
        self.canvas = FigureCanvasTkAgg(self.fig, master = self.root)
        self.canvas.get_tk_widget().grid(row = 2, column=1, columnspan = 3)
        self.canvas.draw()

        slider = tk.Scale(self.root, from_=5.0, to=0.0, variable = self.slide_val, length = 750, digits = 3, resolution = 0.01, command = self.slider_change, showvalue=False)
        slider.grid(row = 1, column = 4, rowspan = 2)

        startButton = tk.Button(self.root, text = 'Start', command = self.collect, height = 5, width = 15)
        startButton.grid(row = 3, column = 1, pady=10)

        stopButton = tk.Button(self.root, text = 'Stop', command = self.stop, height = 5, width = 15)
        stopButton.grid(row = 3, column = 2, pady=10)

        exitButton = tk.Button(self.root, text = 'Exit', command = self.exit, height = 5, width = 15)
        exitButton.grid(row = 3, column = 3, pady=10)
    
    def collect(self):
        self.stop_data.clear()
        if self.var1.get() == 1:
            self.thread = Thread(target = self.generateData)
            self.thread.start()
        else:
            self.thread = Thread(target = self.acquireData)
            self.thread.start()

    def stop(self):
        np.savetxt("data.csv", self.saved_data, delimiter=",")
        self.stop_data.set()
        pass

    def exit(self):
        self.stop()             # stopping thread
        self.root.destroy()     # close GUI
        sys.exit()              # stop script

    def acquireData(self, com = 'COM5', baud = 9600):
        ser = serial.Serial(com, baudrate = baud)

        while(1):
            if (self.stop_data.is_set() == False):
                reading = ser.readline().decode('utf-8').replace('\n', '').replace('\r', '').split(',')
                if '\r' not in reading and '' not in reading:
                    self.data = np.array(list(map(np.float32, reading)))/1024*5
                    self.saved_data = np.vstack((self.saved_data, self.data))
                    self.plot()                
                    self.canvas.draw()
            else:
                break
        ser.close()


    def generateData(self):
        while(1):
            if (self.stop_data.is_set() == False):
                self.data = np.random.randint(0,6, size = (4,))
                self.plot() 
                self.canvas.draw()
            else:
                break
            sleep(0.01)

    def plot(self):
        self.ax.clear()
        color_map = ['y' if (a >= self.slide_val.get()*0.95 and a <= self.slide_val.get()*1.05) else 'g' for a in self.data ]
        self.ax.bar([1,2,3,4], self.data, tick_label = ['1','2','3','4'], width = 0.9, edgecolor = color_map, linewidth = 8, color = 'white')
        self.ax.set_ylim([0,5])
        self.ax.axhline(self.slide_val.get(), color = 'r', linestyle = '-', linewidth = 8) 
        self.ax.get_yaxis().set_visible(False)

    def slider_change(self, event):
        self.plot()
        self.canvas.draw()

