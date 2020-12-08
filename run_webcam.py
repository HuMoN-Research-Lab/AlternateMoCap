# -*- coding: utf-8 -*-
"""
Created on Mon Dec  7 14:16:45 2020

@author: Rontc
"""

import webcam 

#-----------------------------------------------SESSION INFO
#Step 1: Choose a file path and session name
path = r'C:\Users\Rontc\Documents\GitHub\AlternateMocap\\' #add your file path to save data as r'filepath\', and for right now **include a second backslash at the end of your path**
sessionName = 'test2_12_8' #create a session ID for output videos and CSV names

#-----------------------------------------------DETECTION
#Step 2: Cam Detection. Set TRUE to see a list of detected cameras and inputs. Set FALSE once you know your inputs
detect_cam_input = False

if detect_cam_input == True: #don't change this boolean by accident pls
  available_inputs = webcam.checkCams()
  print("You have " + str(len(available_inputs)) + " cameras available at inputs " + str(available_inputs))

#-----------------------------------------------SETUP
#Step 3: Set TRUE to see feeds from each camera. Set FALSE to skip this step
#if TRUE, add camera inputs to setup_inputs list below as [input1,input2,...], based on output from Step 2  
#when testing, press 'q' to individually exit each feed. Camera input number associated with feed is displayed up top
cam_setup = False  
setup_inputs = []

if cam_setup == True: #don't change this boolean by accident pls
    if not setup_inputs:
        raise ValueError('Camera input list (setup_inputs) is empty')
    ulist = []
    for x in setup_inputs:
        u = webcam.videoSetup(x)
        u.start()
        ulist.append(u)
        
    for k in ulist:
        k.join()

#-----------------------------------------------RECORDING
#Step 4: Set TRUE to start the recording process. 
#Press ESCAPE to stop the recording process, and continue onto the time-syncing/editing process
recording = True
record_inputs = [] #the USB input for each camera that you're using 

if recording == True:#don't change this boolean by accident pls
    if not record_inputs:
        raise ValueError('Camera input list (record_inputs) is empty')
    webcam.runCams(record_inputs,path,sessionName) #press ESCAPE to end the recording
