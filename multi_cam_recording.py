# -*- coding: utf-8 -*-
"""
Created on Wed Oct 21 16:07:10 2020

@author: Rontc
"""
import cv2
import threading
import pickle 
import time
import numpy as np
import pandas as pd

global beginTime

class camThread(threading.Thread):
    def __init__(self, previewName, camID,filePath):
        threading.Thread.__init__(self)
        self.previewName = previewName
        self.camID = camID
        self.filePath = filePath
    def run(self):
        print("Starting " + self.previewName)
        camPreview(self.previewName, self.camID, self.filePath)

def camPreview(previewName, camID, filePath):
    global flag 
    flag = False
    cv2.namedWindow(previewName)
    cam = cv2.VideoCapture(camID,cv2.CAP_DSHOW)
    resWidth = 1920
    resHeight = 1080
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, resWidth)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, resHeight)
    fourcc = cv2.VideoWriter_fourcc(*'X264')
    #out = cv2.VideoWriter('C:/Users/Rontc/Documents/HumonLab/framerate/test.mp4',fourcc, 30.0, (640,480))
    out = cv2.VideoWriter(filePath,fourcc, 25.0, (resWidth,resHeight))
    timestamps = []
    #print(timestamps,"printing ts1")
    if cam.isOpened():
        rval, frame = cam.read()
    else:
        rval = False

    while rval:
        if flag:
            with open(previewName, 'wb') as f:
               pickle.dump(timestamps, f)
            break
        cv2.imshow(previewName, frame)
        rval, frame = cam.read()
        out.write(frame)
        timestamps.append(time.time()-beginTime)
        key = cv2.waitKey(20)
        if key == 27:  # exit on ESC
            flag = True 
            with open(previewName, 'wb') as f:
               pickle.dump(timestamps, f)
            break
    cv2.destroyWindow(previewName)


 
beginTime = time.time()
# Create threads as follows, change camID as needed
thread1 = camThread("Camera 1", 0, 'test1.mp4')
thread2 = camThread("Camera 2", 1, 'test2.mp4')
thread3 = camThread("Camera 3", 3, 'test3.mp4')
thread4 = camThread("Camera 4", 4, 'test4.mp4')
#thread3 = camThread("Camera 3", 2)


thread1.start()
thread2.start()
thread3.start()
thread4.start()
#thread3.start()
print()
print("Active threads", threading.activeCount())


thread1.join()
thread2.join()
thread3.join()
thread4.join()

print('finished')

with open("Camera 1", 'rb') as f:
    cam1_list = pickle.load(f)
    
    
with open("Camera 2", 'rb') as f:
    cam2_list = pickle.load(f)    
    
with open("Camera 3", 'rb') as f:
    cam3_list = pickle.load(f)    

with open("Camera 4", 'rb') as f:
    cam4_list = pickle.load(f)        


x = np.array(cam1_list)
y = np.array(cam2_list)
z = np.array(cam3_list)
v = np.array(cam4_list)

a = ({"Camera1":x, "Camera2":y, "Camera3":z, "Camera4":v})
df = pd.DataFrame.from_dict(a, orient = 'index')
df.transpose()
df.to_csv(r"C:\Users\Rontc\Documents\HumonLab\alternate_mocap\spacing_13.csv")

#test = np.row_stack((x, y))#
#p.savez('test_now.csv', x,y)

#print(cam1_list)
#print(cam2_list)

