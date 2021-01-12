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
import tkinter as tk
#import tkMessageBox
from timesync import mastersync
from videoEdit import videoEdit
import sys 

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
    resWidth = 640
    resHeight = 480
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


#Edit the options in lines 70-73 as needed (change csvName and clippedName to prevent overwriting files)

csv_path = r'C:\Users\Rontc\Documents\GitHub\AlternateMoCap\\' #add your file path to save a CSV as r'filepath\', and for right now **include a second backslash at the end of your path**
csvName = 'test2_11_23.csv' #create a filename for the output CSV
clippedName = 'test2_11_23.mp4' #create a base filename for the four edited videos (camera identifiers will be appended onto this base filename)
rawList = ['cam1.mp4','cam2.mp4','cam3.mp4','cam4.mp4'] #create filenames for your raw videos,in order of camera



beginTime = time.time()
# Create threads as follows, change camID as needed
thread1 = camThread("Camera 1", 1, rawList[0])
thread2 = camThread("Camera 2", 2, rawList[1])
thread3 = camThread("Camera 3", 3, rawList[2])
thread4 = camThread("Camera 4", 4, rawList[3])


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
df.to_csv(csv_path+csvName) #change this line to where you want to save a CSV file

"""
top = tk.Tk()
message = tk.Label(text="Here's a look at your start/end times")
start_end = df.iloc[0:4,[0,-1]]


num = tk.Label(text = str(start_end))
str(df.iloc[0:4,0])
label = tk.Label(text = 'Add your desired start and end times below')
entry1 = tk.Entry()
entry2 = tk.Entry()
def getTimes():
    global user_start
    global user_end
    
    user_start = float(entry1.get())
    user_end = float(entry2.get())
     
    
    #print(start, end)
u    top.destroy()

    
button_calc = tk.Button(top, text="OK", command=getTimes)


message.pack()
num.pack()
label.pack()
entry1.pack()
entry2.pack()

#w = tk.Label(top, text="Hello Tkinter!")
#w.pack()
button_calc.pack()


top.mainloop()
"""
#intvl = pickle.loads(intDump)
#print(user_start,user_end)



#print(user_start,user_end)
ft,tt,fr,rd = mastersync(csvName) #enter the starting time, ending time, and CSV file name

top = tk.Tk()
def destroy():
    top.destroy()
def stop():
    top.destroy()
    sys.exit("Quitting Program")
label = tk.Label(text = rd)
button_go = tk.Button(top, text="Proceed", command= destroy)
button_stop = tk.Button(top,text ='Quit',command = stop)

label.pack()
button_go.pack()
button_stop.pack()
top.mainloop()



print()
print('Starting editing')
videoEdit(rawList,clippedName,ft)


print('all done')
#print(end)
#test = np.row_stack((x, y))#
#p.savez('test_now.csv', x,y)

#print(cam1_list)
#print(cam2_list)

