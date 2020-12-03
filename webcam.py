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

def mastersync(filename,camNum,camNames):    
    import pandas as pd
    import numpy as np

    def closeNeighb(camera,point):
        idx = (np.abs(camera - point)).argmin() 
        return idx
    
    df = pd.read_csv (filename)
    #print (df)
    
    arr = df.to_numpy()
    #print(arr)
    stampList = []
    beginList =[]
    endList = []
    for x in camNum:
        cam = arr[x,1:]
        start = cam[0]
        #print(begin)
       
        stop_pt = -1
        stop = cam[stop_pt]
        while np.isnan(stop):
            stop_pt -= 1
            stop = cam[stop_pt]
            
            
        stampList.append(cam)
        beginList.append(start)
        endList.append(stop)

    
    #print(beginList)
    
    begin = np.ceil(max(beginList))
    end = np.floor(min(endList))
    print('end',endList)
    print('test',begin,end)    

    #camera = [cam1,cam2,cam3,cam4]
    
    rate_arr= []
    
  
    n = 0;
    for x in camNum:
      current_cam = stampList[x]
      ss = closeNeighb(current_cam,begin)
      es = closeNeighb(current_cam,end)
      print("using frames:", ss,"-",es,"for",camNames[n])
      n +=1
      intl = current_cam[ss:es]
      test = np.mean(np.diff(intl))
      rate_arr.append(test)
    
    intvl = np.mean(rate_arr)
    mt = np.arange(begin,end,intvl)
   
   
    si = [];
    framelist = mt
    timelist = mt
 
    del_num= [];
    buf_num= [];
    buf_per_list = [];
    del_per_list = [];
    #framelist = [];
    count = 0
    n = 0;

    for y in camNum:
        this_cam = stampList[y]
        si = [];
        sf =[];
    
        count += 1
        #idx_start = closeNeighb(y,mt[0])
        #idx_end = closeNeighb(y,mt[-1])
        #print(idx_start)
        #cam_new = x[idx_start:idx_end]
        for z in mt:
            si_pt = closeNeighb(this_cam, z)
            si.append(si_pt)
            sf = this_cam[si]
            
        print("starting detection:",camNames[n])
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
    col_list = ['Master Timeline'] + camNames
    frameTable.columns = col_list
    timeTable = pd.DataFrame(timelist)
    timeTable.columns = col_list
    framerate = 1/intvl
    results = {'Cam':camNames,'#Del':del_num,'%Del':del_per_list,'#Buf':buf_num,'%Buf':buf_per_list}
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
        
#instructions
#1) Set n_cam
#2) Make sure to add the camera inputs for each webcam you add in iCam        
n_cam= 4 #number of webcams being used
iCam = [1,2,3,4] #the USB input for each camera that you're using 
csv_path = r'C:\Users\Rontc\Documents\GitHub\AlternateMoCap\\' #add your file path to save a CSV as r'filepath\', and for right now **include a second backslash at the end of your path**
csvName = 'test7_12_3.csv' #create a filename for the output CSV
clippedName = 'test7_12_3.mp4' #create a base filename for the four edited videos (camera identifiers will be appended onto this base filename)
#rawList = ['cam1.mp4','cam2.mp4','cam3.mp4','cam4.mp4'] #create filenames for your raw videos,in order of camera



beginTime = time.time()

camNum = range(n_cam)


names = []

camID = []
for x in camNum:
    ids = 'Cam{}'.format(x+1)
    camID.append(ids)
    name = 'cam{}.mp4'.format(x+1)
    names.append(name)    

threads = []


for n in camNum:
    t = camThread(camID[n],iCam[n],names[n])
    t.start()
   
    threads.append(t)

for t in threads:
    t.join()

print('finished')

dataList = []

for e in camNum:
  with open(camID[e], 'rb') as f:
    cam_list = pickle.load(f)
    dataList.append(cam_list)

a = {}    

id_and_time = zip(camID,dataList)  

for cam,data in id_and_time:
    a[cam] = np.array(data)

    
df = pd.DataFrame.from_dict(a, orient = 'index')
df.transpose()
df.to_csv(csv_path+csvName) #change this line to where you want to save a CSV file


ft,tt,fr,rd = mastersync(csvName,camNum,camID) #enter the starting time, ending time, and CSV file name

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
videoEdit(names,clippedName,ft)


print('all done')
