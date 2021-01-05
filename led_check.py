# -*- coding: utf-8 -*-
"""
Created on Mon Nov 16 15:05:43 2020

@author: Rontc
"""
import cv2
import numpy as np
from matplotlib import pyplot as plt 
import pandas as pd
from pathlib import Path

ids = ['Cam1_test3_12_31.mp4','Cam2_test3_12_31.mp4','Cam3_test3_12_31.mp4','Cam4_test3_12_31.mp4']
#ids = ['cam1.mp4','cam2.mp4','cam3.mp4','cam4.mp4']

dirpath = 'C:/Users/Rontc/Documents/GitHub/AlternateMoCap/test3_12_31//'
sessionName = 'edit_test3_12_29'
linkpath = dirpath
csvName = sessionName + '.csv'
datalist = []
#testpath = 'C:/Users/Rontc/Documents/GitHub/AlternateMoCap/test1_12_28/cam1.mp4'
for x in ids:
    #count = 0
    vidcap = cv2.VideoCapture(dirpath + x)#Open video
    vidWidth  = vidcap.get(cv2.CAP_PROP_FRAME_WIDTH) #Get video height
    vidHeight = vidcap.get(cv2.CAP_PROP_FRAME_HEIGHT) #Get video width
    video_resolution = (int(vidWidth),int(vidHeight)) #Create variable for video resolution
    vidLength = vidcap.get(cv2.CAP_PROP_FRAME_COUNT)
    vidfps = vidcap.get(cv2.CAP_PROP_FPS)   
    success,image = vidcap.read() #read a frame
    maxfirstGray = 0 #Intialize the variable for the threshold of the max brightness of beginning of video
    maxsecondGray = 0 #Intialize the variable for the threshold of the max brightness of end of video
    graylist = []
    
    for jj in range(int(vidLength)):#For each frame in the video
        
        success,image = vidcap.read() #read a frame
        if success: #If frame is correctly read
         #   if jj < int(vidLength/3): #If the frame is in the first third of video
                gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY) #Convert image to greyscale
                graylist.append(np.average(gray))
          #      if np.average(gray) > maxfirstGray:#If the average brightness is greater than the threshold
           #         maxfirstGray = np.average(gray)#That average brightness becomes the threshold
            #        firstFlashFrame = jj #Get the frame number of the brightest frame
          #  if jj > int((2*vidLength)/3):
           #     gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY) #Convert image to greyscale
            #    if np.average(gray) > maxsecondGray:#If the average brightness is greater than the threshold
             #       maxsecondGray = np.average(gray)#That average brightness becomes the threshold
              #      secondFlashFrame = jj #Get the frame number of the brightest frame
        else:#If the frame is not correctly read
            print('failure',jj,x)
            continue#Continue
    #print(firstFlashFrame,secondFlashFrame)
    
    xaxis = np.arange(1,vidLength)
    graylist2 = graylist - graylist[0]
    plt.plot(xaxis,graylist2)
    datalist.append(graylist2)
    
#datarry = np.array(datalist)

df = pd.DataFrame(datalist)
#df.to_csv(dirpath+csvName, index = False)