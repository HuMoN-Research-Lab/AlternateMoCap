# -*- coding: utf-8 -*-
"""
Created on Fri Jan  8 12:56:47 2021

@author: Rontc
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import Tk,Label, Button, Frame
import sys
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
   
filename = r'C:\Users\Rontc\Documents\GitHub\AlternateMoCap\test29_01_13\test29_01_13.csv'
#this function is how we find the closest frame to each time point
def CloseNeighb(camera,point): 
    closestPoint = (np.abs(camera - point)).argmin() 
    return closestPoint
run = True
if run: 
    numCamRange = range(4)
    camNames = ['Cam1','Cam2','Cam3','Cam4']
    newFrame = pd.read_csv (filename) #read our CSV file 
    newFrame = newFrame.iloc[:,1:5]
    #newFrame = round(newFrame,2)
    #avgstart = np.mean(newFrame.iloc[0])
    #for h in camNames:
    #    startDif = newFrame[h].iloc[0] - avgstart
    #    print(startDif)
    #    newFrame[h] = newFrame[h] - startDif
    differenceFrame = newFrame.diff(axis = 0)
    fpsFrame = differenceFrame.pow(-1)
    fig = Figure(figsize = [10,10])
    fig.patch.set_facecolor('#F0F0F0')
    a = fig.add_subplot(221)
    a.set_xlabel('Frame')
    a.set_ylabel('Time(s)')
    newFrame.plot(ax = a, title = 'Camera timestamps')
    b = fig.add_subplot(222)
    b.set_xlabel('Frame')
    b.set_ylabel('Frame duration (s)')
    differenceFrame.plot(ax = b, title = 'Camera frame duration') 
    c = fig.add_subplot(223)
    differenceFrame.plot.hist(ax = c, bins=6,alpha = .5, xlim = [0,.1], title = 'Frame interval distribution (s)')
    d = fig.add_subplot(224)
    fpsFrame.plot.hist(ax = d, bins=6,alpha = .5, xlim = [0,40], title = 'Frames per second distribution')
    
    #forplot = newFrame.dropna()
    # =============================================================================
    # fig, axes = plt.subplots(nrows=2, ncols=2)
    # newFrame.plot(ax = axes[0,0], title = 'Camera timestamps')
    # differenceFrame = newFrame.diff(axis = 0)
    # differenceFrame.plot(ax = axes[0,1], title = 'Camera frame duration')
    # 
    # differenceFrame.plot.hist(bins=6,alpha = .5, xlim = [0,.1],ax = axes[1,0], title = 'Frame interval distribution (s)')
    # fpsFrame = differenceFrame.pow(-1)
    # fpsFrame.plot.hist(bins=6,alpha = .5, xlim = [0,40],    ax = axes[1,1], title = 'Frames per second distribution')
    # axes[0,0].set_xlabel('Frame')
    # axes[0,0].set_ylabel('Time (s)')
    # axes[0,1].set_xlabel('Frame')
    # axes[0,1].set_ylabel('Frame duration (s)')
    # 
    # =============================================================================
    #arr = df.to_numpy()
    #print(arr)
    #stampList = [] #store timeframes for each camera
    #beginList =[] #empty list to store the start times for each camera
    #endList = [] #empty list to store the end times for each camera
    #for x in numCamRange: #for each camera that we have
    #    cam = arr[x,1:] #slice out the data for just that camera
    # =============================================================================
    #     startPoint = cam[0] #set start point
    #    
    #  #this section below finds the last non-NAN value for each camera (check if necessary with dataframe)
    #     stopCheckIndex = -1 
    #     stopPoint = cam[stopCheckIndex]
    #     while np.isnan(stopPoint):
    #         stopCheckIndex -= 1
    #         stopPoint = cam[stopCheckIndex]
    #         
    #         
    #     stampList.append(cam) 
    #     beginList.append(startPoint) 
    #     endList.append(stopPoint)
    # =============================================================================
    
    
      
    
    #this section auto-finds the start and end points for our master timeline to the nearest second
    masterTimelineBegin = np.ceil(max(newFrame.iloc[0]))  
    
    lastPoints = []
    for name in camNames:
        cameraLastPoint = newFrame[name][newFrame[name].last_valid_index()]
        lastPoints.append(cameraLastPoint)
    
    
    masterTimelineEnd = np.floor(min(lastPoints))  #find where the fastest camera ended, round down, use that as the end point
    #print('end',endList)
    #print('test',begin,end)    
    
    
    totalFrameRateIntvl= [] #list for storing frame rates for each camera
    
      
    n = 0; #counter for going through camera names
    for x in numCamRange:
      currentCam = newFrame[camNames[x]]
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
        thisCam = newFrame[camNames[y]]
        camTimes = []; #stored times
        camFrames =[]; #stored frames
    
        count += 1
        beginFrame = CloseNeighb(thisCam,masterTimeline[0])
        timeDif = masterTimeline[0] - thisCam[beginFrame]
        thisCam = thisCam + timeDif
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
      
    #return frameTable,timeTable,frameRate,resultTable
    
    # =============================================================================
    # top = tk.Tk()
    # def destroy():
    #     top.destroy()
    # def stop():
    #     top.destroy()
    #     sys.exit("Quitting Program")
    # label = tk.Label(text = resultTable)
    # plotlabel = tk.Label(image = fig)
    # button_go = tk.Button(top, text="Proceed", command= destroy)
    # button_stop = tk.Button(top,text ='Quit',command = stop)
    # 
    # label.pack()
    # button_go.pack()
    # button_stop.pack()
    # top.mainloop()
    # =============================================================================
    # =============================================================================
    class proceedGUI:
        def __init__(self, master, results, figure):
            self.master = master
            self.results = results
            self.figure = figure
            master.title("Choose File Path")
            
          
            bottom_frame = Frame(self.master, height = 1000)
            bottom_frame.pack(side = tk.LEFT)
            self.label = Label(bottom_frame, text= results)
            self.label.pack(side = tk.TOP)
            self.go_button = Button(bottom_frame, text="Proceed", command=self.destroy)
            self.stop_button = Button(bottom_frame, text="Quit", command= self.stop)
       
            self.canvas = FigureCanvasTkAgg(self.figure, master=self.master)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(side=tk.LEFT, fill="both", expand=1)
            
            self.stop_button.pack(side = tk.RIGHT)
            self.go_button.pack(side = tk.RIGHT)
    
            
    
            
    
        def stop(self):
              self.master.destroy()
              sys.exit("Quitting Program")
        
        def destroy(self):
              self.master.destroy()
        
    
    root = Tk()
    
    my_gui = proceedGUI(root,resultTable,fig)
    root.mainloop()

cam2check = newFrame['Cam2']-.01
point2check = masterTimeline[2]
def CloseNeighb2(camera,point):
    pointDiff = np.abs(camera - point)
    closestPoint = pointDiff.argmin()
    candidateCheck = np.abs(pointDiff - pointDiff[closestPoint])
    candidates = [i for i,j in enumerate(candidateCheck) if .01>j>0]
    
    return closestPoint,candidateCheck,candidates
test,test2,test3= CloseNeighb2(cam2check,point2check)

print(cam2check[test],test,point2check)


#def FrameGrouper(newFrame,camNames):
    
    
    