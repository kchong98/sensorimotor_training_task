# a = ['y','y','y','y']
# b = [False, True, False, False]

# def colormap(b):
#     if b == True:
#         return 'g'
#     else:
#         return 'y'

# c = map(colormap, b)
# print(list(c))

from threading import Thread
import time

def timer():
    start = time.time()
    end = time.time()
    while((end-start) <= 3):
        end = time.time()
    print(end - start)

def startThreads():
    a = Thread(target = timer)
    b = Thread(target = timer)
    for i in range(10):
        print(i)
    a.start()
    b.start()

i = Thread(target = startThreads)
i.start()

print('Done')