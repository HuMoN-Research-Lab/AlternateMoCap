# -*- coding: utf-8 -*-
"""
Created on Mon Nov 30 12:48:14 2020

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

def mastersync(filename):    


    def closeNeighb(camera,point):
        idx = (np.abs(camera - point)).argmin() 
        return idx
    
    df = pd.read_csv (filename)
    #print (df)
    
    arr = df.to_numpy()
    #print(arr)
    
    cam1 = arr[0,1:]
    
    cam2 = arr[1,1:]
    
    cam3 = arr[2,1:]
    
    cam4 = arr[3,1:]
    
    begin = np.ceil(min(cam1[0],cam2[0],cam3[0],cam4[0]))
    end = np.floor(np.nanmax([cam1[-1],cam2[-1],cam3[-1],cam4[-1]]))
    print('end',cam1[-1],cam2[-1],cam3[-1],cam4[-1])
    print('test',begin,end)    
    #camera = arr[:,1:]
    camera = [cam1,cam2,cam3,cam4]
    #print(camera)
        
    #begin = 9
    #end = 50
    rate_arr= []
    cam_names = ["Cam A","Cam B","Cam C","Cam D"]
    n = 0;
    for x in camera:
      ss = closeNeighb(x,begin)
      es = closeNeighb(x,end)
      print("using frames:", ss,"-",es,"for",cam_names[n])
      n +=1
      int = x[ss:es]
      test = np.mean(np.diff(int))
      rate_arr.append(test)
    
    intvl = np.mean(rate_arr)
    mt = np.arange(begin,end,intvl)
    #ctest = [cam1]
    
    si = [];
    framelist = mt
    timelist = mt
    #idx_start = closeNeighb(cam1,mt[0])
    #idx_end = closeNeighb(cam1,mt[-1])
    del_num= [];
    buf_num= [];
    buf_per_list = [];
    del_per_list = [];
    #framelist = [];
    count = 0
    n = 0;
    for y in camera:
        si = [];
        sf =[];
    
        count += 1
        #idx_start = closeNeighb(y,mt[0])
        #idx_end = closeNeighb(y,mt[-1])
        #print(idx_start)
        #cam_new = x[idx_start:idx_end]
        for z in mt:
            si_pt = closeNeighb(y, z)
            si.append(si_pt)
            sf = y[si]
            
        print("starting detection:",cam_names[n])
        framelist = np.column_stack((framelist,si))
        timelist = np.column_stack((timelist,sf))
    
        buf_count = 0;
        del_count = 0;
     
        
        for i in range(0,len(si)-1):
            dis = si[i+1] - si[i]
            if dis == 1:
                None
            elif dis == 0:
                buf_count += 1
                #print("Buffer")
                frame1 = abs(mt[i]-sf[i])
                frame2 = abs(mt[i+1]-sf[i])
                if frame1>frame2:
                 framelist[i,count] = -1
                 timelist[i,count] = -1
                else:
                 framelist[i+1,count] = -1;
                 timelist[i+1,count] = -1;
            elif dis > 1:
               del_count += 1
            else:
                
                print("something else happened")
        del_num.append(round(del_count,1))
        buf_num.append(round(buf_count,1))
        print(buf_count,len(framelist))
        buf_per = (buf_count/len(framelist))*100
        del_per = (del_count/len(framelist))*100
        buf_per_list.append(round(buf_per,2))
        del_per_list.append(round(del_per,2))
       
        print(del_num,buf_num,buf_per_list,del_per_list)
        print("deleted frames:",del_count)
        print("buffered frames:",buf_count)
        n +=1
        
        
    frameTable = pd.DataFrame(framelist)   
    col_list = ['Master Timeline','CamA','CamB','CamC','CamD']
    frameTable.columns = col_list
    timeTable = pd.DataFrame(timelist)
    timeTable.columns = col_list
    framerate = 1/intvl
    results = {'Cam':['CamA','CamB','CamC','CamD'],'#Del':del_num,'%Del':del_per_list,'#Buf':buf_num,'%Buf':buf_per_list}
    res_d = pd.DataFrame(results,columns = ['Cam','#Del','%Del','#Buf','%Buf'])
    #print(frameTable,timeTable)
    return frameTable,timeTable,framerate,res_d

def videoEdit(vidList,out_base,ft):
    camList = list(ft.columns[1:len(vidList)+1]) #grab the camera identifiers from the data frame 
    for vid,cam in zip(vidList,camList): #iterate in parallel through camera identifiers and matching videos
        print('Editing '+cam+' from ' +vid)
        #print(cam+'_'+out_path)
        cap = cv2.VideoCapture(vid) #initialize OpenCV capture
        frametable = ft[cam] #grab the frames needed for that camera
        success, image = cap.read() #start reading frames
        fourcc = cv2.VideoWriter_fourcc(*'X264')
        out_path = cam+'_'+out_base #create an output path for the function
        out = cv2.VideoWriter(out_path, fourcc, 25.0, (640,480)) #change resolution as needed
        for frame in frametable: #start looking through the frames we need
            if frame == -1: #this is a buffer frame
                image_new = np.zeros_like(image) #create a blank frame 
                out.write(image_new) #write that frame to the video
            else:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame) #set the video to the frame that we need
                success, image = cap.read()
                out.write(image)
         
        cap.release()
        out.release()
        print('Saved '+out_path)
        print()

csv_path = r'C:\Users\Rontc\Documents\HumonLab\alternate_mocap\\' #add your file path to save a CSV as r'filepath\', and for right now **include a second backslash at the end of your path**
csvName = 'test1_11_30.csv' #create a filename for the output CSV
clippedName = 'test1_11_30.mp4' #create a base filename for the four edited videos (camera identifiers will be appended onto this base filename)
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
