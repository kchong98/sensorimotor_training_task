import tkinter as tk
from turtle import color
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib import gridspec
import matplotlib.pyplot as plt
from threading import Thread, Event
import serial
from serial.tools import list_ports
import pandas as pd
import numpy as np
from time import sleep
import time
import sys


class rot_gui:
    def __init__(self, root):
        super().__init__()
        self.root = root
        self.data = np.array([0, 0])
        self.trial_labels = []
        self.saved_data = np.empty(shape = (5))
        self.ports = list(list_ports.comports())
        self.hold_clear = [False, False]
        self.release = [False, False]
        self.chosen_port = tk.StringVar()
        self.chosen_port.set(self.ports[1])
        self.stop_data = Event()
        self.var1 = tk.IntVar()
        self.slide_val = tk.DoubleVar()
        self.slide_val.set(400.0)
        self.slide_val2 = tk.DoubleVar()
        self.slide_val2.set(400.0)
        self.hold_time = tk.StringVar(value = '3')
        holdLabel = tk.Label(self.root, text = 'Hold Time (s):')
        holdLabel.grid(row = 1, column  = 1)
        self.holdInput = tk.Entry(self.root, textvariable= self.hold_time)
        # self.holdInput.insert('3')
        self.holdInput.grid(row = 1, column = 2)
        c1 = tk.Checkbutton(self.root, text='Generate Data', variable=self.var1, onvalue=1, offvalue=0)
        c1.grid(row = 2, column=1, columnspan=1)
        option_menu = tk.OptionMenu(self.root, self.chosen_port, *self.ports)
        option_menu.grid(row = 4, column = 2, columnspan=2)

        self.fig = plt.figure(figsize = (8,8))
        self.fig.subplots_adjust(top=0.8)
        spec = gridspec.GridSpec(ncols=1, nrows=2,  hspace=0.2, height_ratios=[1, 3])

        self.ax = self.fig.add_subplot(spec[0])
        self.ax2 = self.fig.add_subplot(spec[1])

        self.plot()
        self.canvas = FigureCanvasTkAgg(self.fig, master = self.root)
        self.canvas.get_tk_widget().grid(row = 4, column=1, columnspan = 3)
        self.canvas.draw()

        self.slider = tk.Scale(self.root, from_=0.0, to=1024.0, orient=tk.HORIZONTAL, variable = self.slide_val, length = 750, digits = 3, resolution = 0.01, command = self.slider_change, showvalue=False)
        self.slider.grid(row = 3, column = 1, columnspan= 4)

        self.slider2 = tk.Scale(self.root, from_=1024.0, to=0.0, variable = self.slide_val2, length = 750, digits = 3, resolution = 0.01, command = self.slider_change2, showvalue=False)
        self.slider2.grid(row = 3, column = 5, rowspan = 2)

        startButton = tk.Button(self.root, text = 'Start', command = self.collect, height = 5, width = 15)
        startButton.grid(row = 5, column = 1, pady=10)

        stopButton = tk.Button(self.root, text = 'Stop', command = self.stop, height = 5, width = 15)
        stopButton.grid(row = 5, column = 2, pady=10)

        exitButton = tk.Button(self.root, text = 'Exit', command = self.exit, height = 5, width = 15)
        exitButton.grid(row = 5, column = 3, pady=10)
    
    def collect(self):
        self.slider['state'] = 'disabled'
        self.slider2['state'] = 'disabled'
        self.stop_data.clear()
        if self.var1.get() == 1:
            self.thread = Thread(target = self.generateData)
            self.thread.start()
        else:
            self.thread = Thread(target = self.acquireData, args=(self.chosen_port.get()[0:self.chosen_port.get().index(' ')],))
            self.thread.start()

    def stop(self):
        self.slider['state'] = 'normal'
        self.slider2['state'] = 'normal'
        if self.var1.get() == 0:
            np.savetxt("data.csv", self.saved_data, delimiter=",")
            trial_labels = np.array(self.trial_labels)
            trial_labels = np.unique(trial_labels, axis = 0)
            trial_labels = pd.DataFrame(trial_labels)
            trial_labels[0] = trial_labels[0].astype('int32')
            trial_labels[0] = trial_labels[0] - self.data[0].min()
            trial_labels.set_index(0, inplace=True)
            trial_labels.sort_index(inplace=True, ascending=True)
            trial_labels.to_csv('trials.csv')
        self.stop_data.set()
        pass

    def exit(self):
        self.stop()             # stopping thread
        self.root.destroy()     # close GUI
        sys.exit()              # stop script

    def acquireData(self, com = 'COM4', baud = 9600):
        ser = serial.Serial(com, baudrate = baud)

        while(1):
            if (self.stop_data.is_set() == False):
                reading = ser.readline().decode('utf-8').replace('\n', '').replace('\r', '').split(',')
                if '\r' not in reading and '' not in reading:
                    reading = np.array(list(map(np.float32, reading)))
                    print(f'Reading: {reading}')
                    # print(reading[1],reading[2])
                    # if len(reading) < 3:
                    #     self.data = np.array([0, 0])
                    self.data = reading[0:2]
                    print(f'Data: {self.data}')
                    self.timer_threads()
                    # self.saved_data = np.vstack((self.saved_data, reading))
                    self.plot()                
                    self.canvas.draw()
            else:
                break
        ser.close()


    def generateData(self):
        while(1):
            if (self.stop_data.is_set() == False):
                self.data = np.random.randint(0,6, size=(2,))
                self.data = np.array([1.5, 1.2])
                self.timer_threads()
                self.plot() 
                self.canvas.draw()
            else:
                break
            sleep(0.01)

    def plot(self):
        self.ax.clear()
        self.ax.title.set_text('Rotate')
        # color_map = ['g' if (a >= self.slide_val.get()*0.95 and a <= self.slide_val.get()*1.05) else 'y' for a in self.data]
        color_map = list(map(self.colormap, self.hold_clear, self.release, self.data))
        self.ax.barh([1], self.data[0], height=1, left=None, align='center',tick_label = ['1'], edgecolor = color_map[0], color = 'white', linewidth=5)
        self.ax.set_xlim([0,1024])
        self.ax.set_ylim([0,2])
        self.ax.axvline(self.slide_val.get(), color = 'r', linestyle = '-', linewidth = 20)
        self.ax.get_xaxis().set_visible(False)
        self.ax.get_yaxis().set_visible(False)
        
        self.ax2.clear()
        self.ax2.title.set_text('Slide')
        # color_map = ['g' if (a >= self.slide_val.get()*0.95 and a <= self.slide_val.get()*1.05) else 'y' for a in self.data]
        color_map2 = list(map(self.colormap, self.hold_clear, self.release, self.data))
        self.ax2.bar([1], self.data[1], width=0.8, align='center',tick_label = ['1'], edgecolor = color_map[1], color = 'white', linewidth=5)
        self.ax2.set_xlim([0,2])
        self.ax2.set_ylim([0,1024])
        self.ax2.axhline(self.slide_val2.get(), color = 'r', linestyle = '-', linewidth = 16)
        self.ax2.get_xaxis().set_visible(False)
        self.ax2.get_yaxis().set_visible(False)


    def timer_threads(self):
        threads = [
            Thread(target = self.hold_timer, args = [0]),
            Thread(target = self.hold_timer, args = [1]),
        ]
        # print('CHOOSE THREAD')
        for thread in np.where(((self.data >= self.slide_val.get()*0.9) & (self.data <= self.slide_val.get()*1.1)) | ((self.data >= self.slide_val2.get()*0.9) & (self.data <= self.slide_val2.get()*1.1)))[0]:
            if self.hold_clear[thread] == False and self.release[thread] == False:
                print(f'THREAD {thread}: START')
                self.hold_clear[thread] = True
                if not threads[thread].is_alive():
                    threads[thread].start()


    def hold_timer(self, index):
        # print(f'THREAD {index}: HOLD')
        start = time.time()
        end = time.time()
        while((end-start) <= int(self.hold_time.get())):
            if (self.data[index] >= self.slide_val.get()*0.9) and (self.data[index] <= self.slide_val.get()*1.1):
                temp = np.zeros((2,))
                temp[index] = 1
                temp = temp.tolist()
                temp.insert(0, self.reading[0])
                temp.append('A')
                self.trial_labels.append(temp)

            if ((self.data[index] <= self.slide_val.get()*0.9) or (self.data[index] >= self.slide_val.get()*1.1) or (self.data[index] <= self.slide_val2.get()*0.9) or (self.data[index] >= self.slide_val2.get()*1.1)):
                # print('MOVED!')
                start = time.time()
            end = time.time()
        self.hold_clear[index] = False
        self.release[index] = True
        # print('GOOD!')
        # start = time.time()
        # end = time.time()
        while((self.data[index] >= self.slide_val.get() * 0.9 and self.data[index] <= self.slide_val.get() * 1.1) or (self.data[index] >= self.slide_val2.get() * 0.9 and self.data[index] <= self.slide_val2.get() * 1.1)): #((end-start) <= 3) and
            # continue
            temp = np.zeros((2,))
            temp[index] = 1
            temp = temp.tolist()
            temp.insert(0,self.reading[0])
            temp.append('C')
            self.trial_labels.append(temp)
        # print(f'THREAD {index}: RELEASE')
        self.release[index] = False
        # time.sleep(1)

    def colormap(self, hold, release, data):
        if hold == False and release == False:
            return 'y'
        elif hold == False and release == True and ((data <= self.slide_val.get() * 1.1 and data >= self.slide_val.get() * 0.9) or (data <= self.slide_val2.get() * 1.1 and data >= self.slide_val2.get() * 0.9)):
            return 'g'
        else:
            if (data <= self.slide_val.get()*1.1 and data >= self.slide_val.get()*0.9) or (data <= self.slide_val2.get()*1.1 and data >= self.slide_val2.get()*0.9):
                return 'orange'
            else:
                return 'y'

    def slider_change(self, event):
        self.plot()
        self.canvas.draw()

    def slider_change2(self, event):
        self.plot()
        self.canvas.draw()
