# -*- coding: utf-8 -*-
"""
Created on Mon Dec  7 14:16:45 2020

@author: Rontc
"""

import webcam 
from pathlib import Path

#-----------------------------------------------SESSION INFO
#Choose a file path   
userPath = '' #add custom path here if desired as r'[filepath]\', and for right now **you should have two backslashes at the end of your path**
if not userPath:
        filepath = Path.cwd()
else: 
        filepath = userPath

#---------------------PARAMETERS
#set all desired recording parameters for this session        
sessionName = 'test5_01_19' #create a session ID for output videos and CSV names
exposure = -6
resWidth = 960
resHeight = 720
framerate = 30
codec = 'DIVX' #other codecs to try include H264, DIVX
paramDict = {'exposure':exposure,"resWidth":resWidth,"resHeight":resHeight,'framerate':framerate,'codec':codec}

#-------------------TASK SELECTION
#Select whether to 'detect','setup', or 'record'
#if testing or recording, select camera inputs to record with
#if unsure of camera inputs, use 'detect' to see a list of detected cameras and inputs
task = 'debug' 
cam_inputs = [] #enter inputs as [input1, input2] i.e. [1,2,3,4]

#-----------------------------------------------DETECT
if task == 'detect': 
  available_inputs = webcam.CheckCams()
  print("You have " + str(len(available_inputs)) + " cameras available at inputs " + str(available_inputs))

#-----------------------------------------------SETUP
#when testing, press 'q' to individually exit each feed. Camera input number associated with feed is displayed up top

elif task == 'setup': #don't change this boolean by accident pls
    if not cam_inputs:
        raise ValueError('Camera input list (cam_inputs) is empty')
    ulist = []
    for x in cam_inputs:
        u = webcam.VideoSetup(x,paramDict)
        u.start()
        ulist.append(u)
        
    for k in ulist:
        k.join()

#-----------------------------------------------RECORD
#Press ESCAPE to stop the recording process, and continue onto the time-syncing/editing process

elif task == 'record':#don't change this boolean by accident pls
    recordPath = filepath/sessionName
    recordPath.mkdir(exist_ok='True')
    is_empty = not any(recordPath.iterdir())
    if not is_empty:
            raise RuntimeError(sessionName + ' folder already contains files. check session ID')

    if not cam_inputs:
        raise ValueError('Camera input list (cam_inputs) is empty')
    table = webcam.RunCams(cam_inputs,recordPath,sessionName,paramDict) #press ESCAPE to end the recording
    
elif not task:
    print('No task detected')


elif task == 'debug':
    recordPath = filepath/sessionName
    webcam.DebugTime(sessionName,recordPath)

    
else:
    print('Unrecognized task: please enter task as "detect","setup",or "record"')
