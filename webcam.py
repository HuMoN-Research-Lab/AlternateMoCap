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
class CamThread(threading.Thread): 
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
        CamPreview(self.camID, self.camInput, self.videoName,self.filePath,self.beginTime,self.parameterDictionary)

#the recording function that each threaded camera object runs
def CamPreview(camID, camInput, videoName,filepath,beginTime,parameterDictionary):
    #the flag is triggered when the user shuts down one webcam to shut down the rest. 
    #normally I'd try to avoid global variables, but in this case it's 
    #necessary, since each webcam runs as it's own object.
    global flag 
    flag = False 
    
    cv2.namedWindow(camID) #name the preview window for the camera its showing
    cam = cv2.VideoCapture(camInput,cv2.CAP_DSHOW) #create the video capture object
    #if not cam.isOpened():
    #         raise RuntimeError('No camera found at input '+ str(camID)) 
    #pulling out all the dictionary paramters 
    exposure = parameterDictionary.get('exposure')
    resWidth = parameterDictionary.get('resWidth')
    resHeight = parameterDictionary.get('resHeight')
    framerate = parameterDictionary.get('framerate')
    codec = parameterDictionary.get('codec')
    
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, resWidth)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, resHeight)
    cam.set(cv2.CAP_PROP_EXPOSURE, exposure)
    fourcc = cv2.VideoWriter_fourcc(*codec)
    rawPath = filepath/'RawVideos' #creating a RawVideos folder
    rawPath.mkdir(parents = True, exist_ok = True)
    
    recordPath = str(rawPath/videoName) #create a save path for each video to the RawVideos folders
    out = cv2.VideoWriter(recordPath,fourcc, framerate, (resWidth,resHeight))
    timeStamps = [] #holds the timestamps 

    if cam.isOpened():
        success, frame = cam.read()
    else:
        success = False

    while success: #while the camera is opened, record the data until the escape button is hit 
        if flag: #when the flag is triggered, stop recording and dump the data
            with open(camID, 'wb') as f:
               pickle.dump(timeStamps, f)
            break
        
        cv2.imshow(camID, frame)
        success, frame = cam.read()
        out.write(frame)
        timeStamps.append(time.time()-beginTime) #add each timestamp to the list
    
        key = cv2.waitKey(20)
        if key == 27:  # exit on ESC
            flag = True #set flag to true to shut down all other webcams
            with open(camID, 'wb') as f:
               pickle.dump(timeStamps, f) #dump the data
            break
    cv2.destroyWindow(camID)

#this is how we sync our time frames, based on our recorded timestamps
def TimeSync(filename,numCamRange,camNames):    
   
#this function is how we find the closest frame to each time point
    def CloseNeighb(camera,point): 
        closestPoint = (np.abs(camera - point)).argmin() 
        return closestPoint
    
    df = pd.read_csv (filename) #read our CSV file 
  
    arr = df.to_numpy()
    #print(arr)
    stampList = [] #store timeframes for each camera
    beginList =[] #empty list to store the start times for each camera
    endList = [] #empty list to store the end times for each camera
    for x in numCamRange: #for each camera that we have
        cam = arr[x,1:] #slice out the data for just that camera
        startPoint = cam[0] #set start point
       
     #this section below finds the last non-NAN value for each camera (check if necessary with dataframe)
        stopCheckIndex = -1 
        stopPoint = cam[stopCheckIndex]
        while np.isnan(stopPoint):
            stopCheckIndex -= 1
            stopPoint = cam[stopCheckIndex]
            
            
        stampList.append(cam) 
        beginList.append(startPoint) 
        endList.append(stopPoint)

    
  
    
    #this section auto-finds the start and end points for our master timeline to the nearest second
    masterTimelineBegin = np.ceil(max(beginList)) #find where slowest camera started, round up, use that as the start point
    masterTimelineEnd = np.floor(min(endList)) #find where the fastest camera ended, round down, use that as the end point
    #print('end',endList)
    #print('test',begin,end)    

    
    totalFrameRateIntvl= [] #list for storing frame rates for each camera
    
  
    n = 0; #counter for going through camera names
    for x in numCamRange:
      currentCam = stampList[x]  
      #finds the closest point in each camera to the start and end points of our timeline
      currentCamStart = CloseNeighb(currentCam,masterTimelineBegin) 
      currentCamEnd = CloseNeighb(currentCam,masterTimelineEnd)
      print("using frames:", currentCamStart,"-",currentCamEnd,"for",camNames[n])
      n +=1
      currentCamTimeline = currentCam[currentCamStart:currentCamEnd] #grab the times from start to finish for each camera
      currentCamFrameInterval = np.mean(np.diff(currentCamTimeline)) #calculate the interval between each frame and take the mean 
      totalFrameRateIntvl.append(currentCamFrameInterval) #add interval to list 
    
    totalAverageIntvl = np.mean(totalFrameRateIntvl) #find the total average interval across all cameras
    masterTimeline = np.arange(masterTimelineBegin,masterTimelineEnd,totalAverageIntvl) #build a master timeline with the average interval
   
    #now we start the syncing process
  
    frameList = masterTimeline #start a list of frames, with the first row being our master timeline
    timeList = masterTimeline #start a list of timestamps,with the first row being our master timeline
 
    delNum= []; #stores number of deleted frames/camera
    bufNum= []; #stores number of buffered frames/camera
    bufPercentList = []; #stores percentage of deleted frames/camera
    delPercentList = []; #stores percentage of buffered frames/camera
    
    count = 0 #Keeps track of what frame we're on (I think?)
    n = 0; #I don't remember why I did this but I'm sure I'll figure it out later

    for y in numCamRange:
        thisCam = stampList[y]
        camTimes = []; #stored times
        camFrames =[]; #stored frames
    
        count += 1
       
        for z in masterTimeline: #for each point in the master timeline
            closestFrame = CloseNeighb(thisCam, z) #find the closest frame in this camera to each point of the master timeline
            camFrames.append(closestFrame) #add that frame to the list
            camTimes.append(thisCam[closestFrame]) #find the time corresponding to this frame
            
        print("starting detection:",camNames[n]) #now to start finding deleted/buffered slides
        frameList = np.column_stack((frameList,camFrames)) #update our framelist with our new frames
        timeList = np.column_stack((timeList,camTimes)) #update our timelist 
    
        #start counters for the number of buffered and deleted slides
        bufCount = 0;
        delCount = 0;
      
        for i in range(0,len(camFrames)-1): 
            distanceBetweenFrames = camFrames[i+1] - camFrames[i] #find the distance between adjacent frames
            if distanceBetweenFrames == 1: #these frames are consecutive, do nothing
                None 
            elif distanceBetweenFrames == 0: #we have a buffered slide
                bufCount += 1
                #this section looks at our two timepoints, and finds the which point on the master timeline is closest 
                frame1 = abs(masterTimeline[i]-camTimes[i])
                frame2 = abs(masterTimeline[i+1]-camTimes[i])
                #finds which frame is closest, and sets the other frame as a buffer (indicated by the -1)
                if frame1>frame2:
                 frameList[i,count] = -1
                 timeList[i,count] = -1
                else:
                 frameList[i+1,count] = -1;
                 timeList[i+1,count] = -1;
            elif distanceBetweenFrames > 1: #deletion
               delCount += 1
            else:
                
                print("something else happened")
        #update and calculate our percentages and numbers for buffers/deletions
        delNum.append(round(delCount,1))
        bufNum.append(round(bufCount,1))
        print(bufCount,len(frameList))
        bufPercent = (bufCount/len(frameList))*100
        delPercent = (delCount/len(frameList))*100
        bufPercentList.append(round(bufPercent,2))
        delPercentList.append(round(delPercent,2))
       
        print(delNum,bufNum,bufPercentList,delPercentList)
        print("deleted frames:",delCount)
        print("buffered frames:",bufCount)
        n +=1
        
    #create our data frame for both times and frames    
    frameTable = pd.DataFrame(frameList)   
    columnNames = ['Master Timeline'] + camNames
    frameTable.columns = columnNames
    timeTable = pd.DataFrame(timeList)
    timeTable.columns = columnNames
    frameRate = 1/totalAverageIntvl #calculates our framerate 
    results = {'Cam':camNames,'#Del':delNum,'%Del':delPercentList,'#Buf':bufNum,'%Buf':bufPercentList}
    resultTable = pd.DataFrame(results,columns = ['Cam','#Del','%Del','#Buf','%Buf'])
  
    return frameTable,timeTable,frameRate,resultTable
 
#function to trim our videos 
def VideoEdit(filepath, vidList,sessionName,ft,parameterDictionary):
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
        frameTable = ft[cam] #grab the frames needed for that camera
        success, image = cap.read() #start reading frames
        fourcc = cv2.VideoWriter_fourcc(*codec)
        saveName = sessionName +'_synced_' + cam + '.mp4' 
        syncedPath = filepath/'SyncedVideos'
        syncedPath.mkdir(parents = True, exist_ok = True)
        savePath = str(syncedPath/saveName) #create an output path for the function
        out = cv2.VideoWriter(savePath, fourcc, framerate, (resWidth,resHeight)) #change resolution as needed
        for frame in tqdm(frameTable, leave = True): #start looking through the frames we need
            if frame == -1: #this is a buffer frame
                blankFrame = np.zeros_like(image) #create a blank frame 
                out.write(blankFrame) #write that frame to the video
            else:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame) #set the video to the frame that we need
                success, image = cap.read()
                out.write(image)
         
        cap.release()
        out.release()
        print('Saved '+ savePath)
        print()
        
       
#function to run all these above functions together
def RunCams(camInputs,filepath,sessionName,parameterDictionary):
    csvName = sessionName + '.csv' #create our csv filename
    
    beginTime = time.time()
    numCams = len(camInputs) #number of cameras 
    numCamRange = range(numCams) #a range for the number of cameras that we have
    videoNames = []
    camIDs = []
    for x in numCamRange: #create names for each of the initial untrimmed videos 
        singleCamID = 'Cam{}'.format(x+1)
        camIDs.append(singleCamID) #creates IDs for each camera based on the number of cameras entered
        singleVidName = 'raw_cam{}.mp4'.format(x+1)
        videoNames.append(singleVidName)    
    
    threads = []
    
    for n in numCamRange: #starts recording video, opens threads for each camera
        camRecordings = CamThread(camIDs[n],camInputs[n],videoNames[n],filepath,beginTime,parameterDictionary)
        camRecordings.start()
       
        threads.append(camRecordings) 
    
    for camRecordings in threads:
        camRecordings.join() #make sure that one thread ending doesn't immediately end all the others (before they can dump data in a pickle file)
    
    print('finished')
    
    timeStampList = [] 
    
    for e in numCamRange: #open the saved pickle file for each camera, and add the timestamps to the dataList list
      with open(camIDs[e], 'rb') as f:
        camTimeList = pickle.load(f)
        timeStampList.append(camTimeList)
    
    timeDictionary = {}  #our dictionary   
        
    id_and_time = zip(camIDs,timeStampList)  
    
    for cam,data in id_and_time:
        timeDictionary[cam] = np.array(data)  #create a dictionary that holds the timestamps for each camera 
    
        
    df = pd.DataFrame.from_dict(timeDictionary, orient = 'index') #create a data frame from this dictionary
    dfT = df.transpose()
    csvPath = filepath/csvName
    df.to_csv(csvPath) #turn dataframe into a CSV
    
    
    frameTable,timeTable,frameRate,resultsTable = TimeSync(csvPath,numCamRange,camIDs) #start the timesync process
    
    #this message shows you your percentages and asks if you would like to continue or not. shuts down the program if no
    top = tk.Tk()
    def destroy():
        top.destroy()
    def stop():
        top.destroy()
        sys.exit("Quitting Program")
    label = tk.Label(text = resultsTable)
    button_go = tk.Button(top, text="Proceed", command= destroy)
    button_stop = tk.Button(top,text ='Quit',command = stop)
    
    label.pack()
    button_go.pack()
    button_stop.pack()
    top.mainloop()
    
    
    
    print()
    print('Starting editing')
    #start editing the videos 
    VideoEdit(filepath,videoNames,sessionName,frameTable,parameterDictionary)
    
    
    print('all done')

def TestDevice(source):
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

def CheckCams():
    openCamList = []
    for x in range(100):        
       openCamera = TestDevice(x)
       if openCamera is not None:
          openCamList.append(openCamera)
    
    return openCamList
       
class VideoSetup(threading.Thread):
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
