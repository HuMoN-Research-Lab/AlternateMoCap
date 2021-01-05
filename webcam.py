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
from tqdm import tqdm 
import sys 

global beginTime


#create a camera object that can be threaded
class camThread(threading.Thread): 
    def __init__(self,camID,camInput,videoName,filePath,beginTime,parameterDictionary):
        threading.Thread.__init__(self)
        self.camID = camID
        self.camInput = camInput
        self.videoName = videoName
        self.filePath = filePath
        self.beginTime = beginTime
        self.parameterDictionary = parameterDictionary
    def run(self):
        print("Starting " + self.camID)
        camPreview(self.camID, self.camInput, self.videoName,self.filePath,self.beginTime,self.parameterDictionary)

#the recording function that each threaded camera object runs
def camPreview(camID, camInput, videoName,filepath,beginTime,parameterDictionary):
    #the flag is triggered when the user shuts down one webcam to shut down the rest. 
    #normally we'd try to avoid global variables, but in this case it's 
    #necessary, since each webcam runs as it's own object.
    global flag 
    flag = False 
    
    cv2.namedWindow(camID)
    cam = cv2.VideoCapture(camInput,cv2.CAP_DSHOW)
    #if not cam.isOpened():
    #         raise RuntimeError('No camera found at input '+ str(camID)) 
  
    exposure = parameterDictionary.get('exposure')
    resWidth = parameterDictionary.get('resWidth')
    resHeight = parameterDictionary.get('resHeight')
    framerate = parameterDictionary.get('framerate')
    codec = parameterDictionary.get('codec')
    
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, resWidth)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, resHeight)
    cam.set(cv2.CAP_PROP_EXPOSURE, exposure)
    fourcc = cv2.VideoWriter_fourcc(*codec)
    rawPath = filepath/'RawVideos'
    rawPath.mkdir(parents = True, exist_ok = True)
    recordPath = str(rawPath/videoName)
    out = cv2.VideoWriter(recordPath,fourcc, framerate, (resWidth,resHeight))
    timestamps = [] #holds the timestamps 

    if cam.isOpened():
        rval, frame = cam.read()
    else:
        rval = False

    while rval:
        if flag: #when the flag is triggered, stop recording and dump the data
            with open(camID, 'wb') as f:
               pickle.dump(timestamps, f)
            break
        
        cv2.imshow(camID, frame)
        rval, frame = cam.read()
        out.write(frame)
        timestamps.append(time.time()-beginTime) #add each timestamp to the list
    
        key = cv2.waitKey(20)
        if key == 27:  # exit on ESC
            flag = True #set flag to true to shut down all other webcams
            with open(camID, 'wb') as f:
               pickle.dump(timestamps, f) #dump the data
            break
    cv2.destroyWindow(camID)

#this is how we sync our time frames, based on our recorded timestamps
def mastersync(filename,camNum,camNames):    
   
#this function is how we find the closest frame to each time point
    def closeNeighb(camera,point): 
        idx = (np.abs(camera - point)).argmin() 
        return idx
    
    df = pd.read_csv (filename) #read our CSV file 
  
    arr = df.to_numpy()
    #print(arr)
    stampList = [] #store timeframes for each camera
    beginList =[] #empty list to store the start times for each camera
    endList = [] #empty list to store the end times for each camera
    for x in camNum: #for each camera that we have
        cam = arr[x,1:] #slice out the data for just that camera
        start = cam[0] #set start point
       
     #this section below find the last non-NAN value for each camera   
        stop_pt = -1
        stop = cam[stop_pt]
        while np.isnan(stop):
            stop_pt -= 1
            stop = cam[stop_pt]
            
            
        stampList.append(cam) 
        beginList.append(start) 
        endList.append(stop)

    
  
    
    #this section auto-finds the start and end points for our master timeline to the nearest second
    begin = np.ceil(max(beginList)) #find where slowest camera started, round up, use that as the start point
    end = np.floor(min(endList)) #find where the fastest camera ended, round down, use that as the end point
    #print('end',endList)
    #print('test',begin,end)    

    
    int_arr= [] #list for storing frame rates for each camera
    
  
    n = 0; #counter for going through camera names
    for x in camNum:
      current_cam = stampList[x]  
      #finds the closest point in each camera to the start and end points of our timeline
      ss = closeNeighb(current_cam,begin) 
      es = closeNeighb(current_cam,end)
      print("using frames:", ss,"-",es,"for",camNames[n])
      n +=1
      cam_timeline = current_cam[ss:es] #grab the times from start to finish for each camera
      interval = np.mean(np.diff(cam_timeline)) #calculate the interval between each frame and take the mean 
      int_arr.append(interval) #add interval to list 
    
    avg_int = np.mean(int_arr) #find the total average interval across all cameras
    mt = np.arange(begin,end,avg_int) #build a master timeline with the average interval
   
    #now we start the syncing process
  
    framelist = mt #start a list of frames, with the first row being our master timeline
    timelist = mt #start a list of timestamps,with the first row being our master timeline
 
    del_num= []; #stores number of deleted frames/camera
    buf_num= []; #stores number of buffered frames/camera
    buf_per_list = []; #stores percentage of deleted frames/camera
    del_per_list = []; #stores percentage of buffered frames/camera
    
    count = 0 #Keeps track of what frame we're on (I think?)
    n = 0; #I don't remember why I did this but I'm sure I'll figure it out later

    for y in camNum:
        this_cam = stampList[y]
        st = []; #stored times
        sf =[]; #stored frames
    
        count += 1
       
        for z in mt: #for each point in the master timeline
            sf_pt = closeNeighb(this_cam, z) #find the closest frame in this camera to each point of the master timeline
            sf.append(sf_pt) #add that frame to the list
            st = this_cam[sf] #find the time corresponding to this frame
            
        print("starting detection:",camNames[n]) #now to start finding deleted/buffered slides
        framelist = np.column_stack((framelist,sf)) #update our framelist with our new frames
        timelist = np.column_stack((timelist,st)) #update our timelist 
    
        #start counters for the number of buffered and deleted slides
        buf_count = 0;
        del_count = 0;
      
        for i in range(0,len(sf)-1): 
            dis = sf[i+1] - sf[i] #find the distance between adjacent frames
            if dis == 1: #these frames are consecutive, do nothing
                None 
            elif dis == 0: #we have a buffered slide
                buf_count += 1
                #this section looks at our two timepoints, and finds the which point on the mater timeline is closest 
                frame1 = abs(mt[i]-st[i])
                frame2 = abs(mt[i+1]-st[i])
                #finds which frame is closest, and sets the other frame as a buffer (indicated by the -1)
                if frame1>frame2:
                 framelist[i,count] = -1
                 timelist[i,count] = -1
                else:
                 framelist[i+1,count] = -1;
                 timelist[i+1,count] = -1;
            elif dis > 1: #deletion
               del_count += 1
            else:
                
                print("something else happened")
        #update and calculate our percentages and numbers for buffers/deletions
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
        
    #create our data frame for both times and frames    
    frameTable = pd.DataFrame(framelist)   
    col_list = ['Master Timeline'] + camNames
    frameTable.columns = col_list
    timeTable = pd.DataFrame(timelist)
    timeTable.columns = col_list
    framerate = 1/avg_int #calculates our framerate 
    results = {'Cam':camNames,'#Del':del_num,'%Del':del_per_list,'#Buf':buf_num,'%Buf':buf_per_list}
    res_d = pd.DataFrame(results,columns = ['Cam','#Del','%Del','#Buf','%Buf'])
  
    return frameTable,timeTable,framerate,res_d
 
#function to trim our videos 
def videoEdit(filepath, vidList,out_base,ft,parameterDictionary):
    camList = list(ft.columns[1:len(vidList)+1]) #grab the camera identifiers from the data frame 
    resWidth = parameterDictionary.get('resWidth')
    resHeight = parameterDictionary.get('resHeight')
    framerate = parameterDictionary.get('framerate')
    codec = parameterDictionary.get('codec')
    for vid,cam in zip(vidList,camList): #iterate in parallel through camera identifiers and matching videos
        print('Editing '+cam+' from ' +vid)
        #print(cam+'_'+out_path)
        rawPath = filepath/'RawVideos'
        cap = cv2.VideoCapture(str(rawPath/vid)) #initialize OpenCV capture
        frametable = ft[cam] #grab the frames needed for that camera
        success, image = cap.read() #start reading frames
        fourcc = cv2.VideoWriter_fourcc(*codec)
        out_name = out_base+'_' + cam + '.mp4'  #create an output path for the function
        syncedPath = filepath/'SyncedVideos'
        syncedPath.mkdir(parents = True, exist_ok = True)
        out_path = str(syncedPath/out_name)
        out = cv2.VideoWriter(out_path, fourcc, framerate, (resWidth,resHeight)) #change resolution as needed
        for frame in tqdm(frametable): #start looking through the frames we need
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
        
       
#function to run all these above functions together
def runCams(camInputs,filepath,sessionName,parameterDictionary):
    csvName = sessionName + '.csv' #create our csv filename
    clippedName = sessionName + '.mp4' #create our final video names
    
    beginTime = time.time()
    n_cam = len(camInputs) #number of cameras 
    camNum = range(n_cam) #a range for the number of cameras that we have
    videoNames = []
    camID = []
    for x in camNum: #create names for each of the initial untrimmed videos 
        ids = 'Cam{}'.format(x+1)
        camID.append(ids) #creates IDs for each camera based on the number of cameras entered
        vidName = 'cam{}.mp4'.format(x+1)
        videoNames.append(vidName)    
    
    threads = []
    
    for n in camNum: #starts recording video, opens threads for each camera
        t = camThread(camID[n],camInputs[n],videoNames[n],filepath,beginTime,parameterDictionary)
        t.start()
       
        threads.append(t) 
    
    for t in threads:
        t.join() #make sure that one thread ending doesn't immediately end all the others (before they can dump data in a pickle file)
    
    print('finished')
    
    dataList = [] 
    
    for e in camNum: #open the saved pickle file for each camera, and add the timestamps to the dataList list
      with open(camID[e], 'rb') as f:
        cam_list = pickle.load(f)
        dataList.append(cam_list)
    
    a = {}  #our dictionary   
        
    id_and_time = zip(camID,dataList)  
    
    for cam,data in id_and_time:
        a[cam] = np.array(data)  #create a dictionary that holds the timestamps for each camera 
    
        
    df = pd.DataFrame.from_dict(a, orient = 'index') #create a data frame from this dictionary
    df.transpose()
    csvPath = filepath/csvName
    df.to_csv(csvPath) #turn dataframe into a CSV
    
    
    ft,tt,fr,rd = mastersync(csvPath,camNum,camID) #start the timesync process
    
    #this message shows you your percentages and asks if you would like to continue or not. shuts down the program if no
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
    #start editing the videos 
    videoEdit(filepath,videoNames,sessionName,ft,parameterDictionary)
    
    
    print('all done')

def testDevice(source):
   cap = cv2.VideoCapture(source,cv2.CAP_DSHOW) 
   #if cap is None or not cap.isOpened():
       #print('Warning: unable to open video source: ', source)
   
   if cap.isOpened():
        print('Opened: ',source)
        print('Exposure: '+ str(cap.get(cv2.CAP_PROP_EXPOSURE)))
        #time.sleep(3)
        cap.release()
        cv2.destroyAllWindows() 
        open_cam = source
        return open_cam
   else:
        return None 

def checkCams():
    open_list = []
    for x in range(100):        
       open_c = testDevice(x)
       if open_c is not None:
          open_list.append(open_c)
    
    return open_list
       
class videoSetup(threading.Thread):
     def __init__(self, camID,parameterDictionary):
         self.camID = camID
         self.parameterDictionary = parameterDictionary
         threading.Thread.__init__(self)
     def run(self):
        #print("Starting " + self.previewName)
         self.record(self.parameterDictionary)
     def record(self,parameterDictionary):
         exposure = parameterDictionary.get('exposure')
         resWidth = parameterDictionary.get('resWidth')
         resHeight = parameterDictionary.get('resHeight')
         camName = "Camera" + str(self.camID)
         
         cv2.namedWindow(camName)
         cap = cv2.VideoCapture(self.camID,cv2.CAP_DSHOW)
         cap.set(cv2.CAP_PROP_FRAME_WIDTH, resWidth)
         cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resHeight)
         cap.set(cv2.CAP_PROP_EXPOSURE, exposure)
         #print('exposure',cap.get(cv2.CAP_PROP_EXPOSURE))
         #if not cap.isOpened():
          #   raise RuntimeError('No camera found at input '+ str(self.camID)) 
         while True:
             ret1,frame1 = cap.read()
             if ret1 ==True:
                 cv2.imshow(camName,frame1)
                 if cv2.waitKey(1) & 0xFF== ord('q'):
                    break 
         
             else:
                break
         cv2.destroyWindow(camName)
