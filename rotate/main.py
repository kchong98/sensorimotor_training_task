from threading import Thread
from rotateGUI import *
import serial
import tkinter as tk

if __name__ == '__main__':
    root1 = tk.Tk()
    my_gui = rot_gui(root1)
    root1.mainloop()