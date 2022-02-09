from threading import Thread
from GUI import *
import serial
import tkinter as tk

if __name__ == '__main__':
    root = tk.Tk()
    my_gui = gui(root)
    root.mainloop()