# -*- coding: utf-8 -*-
"""
Created on Mon Dec  7 14:16:45 2020

@author: Rontc
"""

import webcam 
from pathlib import Path

#-----------------------------------------------SESSION INFO
#Step 1: Choose a file path and session name   


userPath = '' #add custom path here if desired as r'[filepath]\', and for right now **you should have two backslashes at the end of your path**
if not userPath:
        filepath = Path.cwd()
else: 
        filepath = userPath
        
sessionName = 'test33_01_05' #create a session ID for output videos and CSV names
exposure = -4
resWidth = 640
resHeight = 480
framerate = 25
codec = 'X264' #other codecs to try include H264, DIVX

paramDict = {'exposure':exposure,"resWidth":resWidth,"resHeight":resHeight,'framerate':framerate,'codec':codec}

#-----------------------------------------------DETECTION
#Step 2: Cam Detection. Set TRUE to see a list of detected cameras and inputs. Set FALSE once you know your inputs
detect_cam_input = False

if detect_cam_input == True: #don't change this boolean by accident pls
  available_inputs = webcam.CheckCams()
  print("You have " + str(len(available_inputs)) + " cameras available at inputs " + str(available_inputs))

#-----------------------------------------------SETUP
#Step 3: Set TRUE to see feeds from each camera. Set FALSE to skip this step
#if TRUE, add camera inputs to setup_inputs list below as [input1,input2,...], based on output from Step 2  
#when testing, press 'q' to individually exit each feed. Camera input number associated with feed is displayed up top
cam_setup = False  
setup_inputs = [1,2,3,4]

if cam_setup == True: #don't change this boolean by accident pls
    if not setup_inputs:
        raise ValueError('Camera input list (setup_inputs) is empty')
    ulist = []
    for x in setup_inputs:
        u = webcam.VideoSetup(x,paramDict)
        u.start()
        ulist.append(u)
        
    for k in ulist:
        k.join()

#-----------------------------------------------RECORDING
#Step 4: Set TRUE to start the recording process. 
#Press ESCAPE to stop the recording process, and continue onto the time-syncing/editing process
recording = True
record_inputs = [1,2,3,4] #the USB input for each camera that you're using 



if recording == True:#don't change this boolean by accident pls
    recordPath = filepath/sessionName
    recordPath.mkdir(exist_ok='True')
    is_empty = not any(recordPath.iterdir())
    #if not is_empty:
     #       raise RuntimeError(sessionName + ' folder already contains files. check session ID')

    if not record_inputs:
        raise ValueError('Camera input list (record_inputs) is empty')
    webcam.RunCams(record_inputs,recordPath,sessionName,paramDict) #press ESCAPE to end the recording
