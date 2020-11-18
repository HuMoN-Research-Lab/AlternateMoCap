# -*- coding: utf-8 -*-
"""
Created on Wed Nov 18 12:29:22 2020

@author: Rontc
"""
import cv2
import numpy as np
from timesync import mastersync


def videoEdit(vidList,out_base,ft):
    camList = list(ft.columns[1:len(vidList)+1]) #grab the camera identifiers from the data frame 
    for vid,cam in zip(vidList,camList): #iterate in parallel through camera identifiers and matching videos
        print('Editing '+cam+' from ' +vid)
        #print(cam+'_'+out_path)
        cap = cv2.VideoCapture(vid) #initialize OpenCV capture
        frametable = ft[cam] #grab the frames needed for that camera
        success, image = cap.read() #start reading frames
        fourcc = cv2.VideoWriter_fourcc(*'X264')
        out_path = cam+'_'+out_base+'.mp4' #create an output path for the function
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
  


#Order of Operations
#1 Run the mastersync function on your CSV file 
#2 Make sure the video resolution in the videoEdit function in "out = cv2.VideoWriter...". Will try to hardcode this as we move forward
#2 Make sure the entries in vidList match the exported video files from your 
#  recordings and are listed in the order of CamA/CamB/CamC/CamD
#3 Choose a file name for your four output videos. They'll save as CamA_[insert file name], CamB_[insert file name] and so on
#4 Run the video edit function


ft,tt,fr = mastersync(4,15,'test1_11_18.csv') #enter the starting time, ending time, and CSV file name
vidList = ['test1.mp4','test2.mp4','test3.mp4','test4.mp4'] 
path = 'test1_11_18'
print()
print('Starting editing')
videoEdit(vidList,path,ft)

    