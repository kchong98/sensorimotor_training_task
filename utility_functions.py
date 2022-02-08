import serial
import numpy as np
from time import sleep

def acquireData(com = 'COM5', baud = 9600):
    while(1):
        ser = serial.Serial(com, baudrate = baud)
        data = serial.readline()
    ser.close()
    pass

def generateData():
    while(1):
        data = np.random.randint(0,5, size = (4,))
        print(data)
        sleep(0.01)

if __name__ == '__main__':
    generateData()