# -*- coding: utf-8 -*-
"""
Created on Mon Dec  7 14:16:45 2020

@author: Rontc
"""

import webcam 
from pathlib import Path
import datetime
import os 
import cv2

#-----------------------------------------------SESSION INFO
#Choose a file path   
userPath = '' #add custom path here if desired as r'[filepath]\', and for right now **you should have two backslashes at the end of your path**
if not userPath:
        filepath = Path.cwd()
else: 
        filepath = userPath

#------------------ROTATION DEFINITIONS
rotate0 = None
rotate90 = cv2.ROTATE_90_CLOCKWISE
rotate180 = cv2.ROTATE_180
rotate270 = cv2.ROTATE_90_COUNTERCLOCKWISE

#---------------------PARAMETERS
sessionID =  '' #enter custom ID here

if not sessionID: #if no custom ID is entered, one will be generated (as sesh[time of recording in hours:minutes:seconds]_[month]_[date])
    sessionID = datetime.datetime.now().strftime("sesh_%y_%m_%d_%H%M%S")
if os.getenv('COMPUTERNAME') == 'DESKTOP-DCG6K4F': #Jon's Work PC    
    #set all desired recording parameters for this session        
    #sessionID = 'test1_01_21' #create a session ID for output videos and CSV names
    exposure = -6
    resWidth = 960
    resHeight = 720
    framerate = 30
    codec = 'DIVX' #other codecs to try include H264, DIVX
    paramDict = {'exposure':exposure,"resWidth":resWidth,"resHeight":resHeight,'framerate':framerate,'codec':codec}
    #for rotation inputs, specify a rotation for each camera as either: rotation0, rotation90, rotation180, or rotation270
    #if rotating any camera, each camera needs to have a rotation input. i.e. [rotation90,rotation0,rotation0]
    #if no rotations are needed, just have rotation_input = [] (an empty array)
    rotation_input = []
else:
    exposure = -6
    resWidth = 640
    resHeight = 480
    framerate = 30
    codec = 'DIVX' #other codecs to try include H264, DIVX
    paramDict = {'exposure':exposure,"resWidth":resWidth,"resHeight":resHeight,'framerate':framerate,'codec':codec}
    rotation_input = []
#-------------------TASK SELECTION
#Select whether to 'detect','setup', or 'record'
#if testing or recording, select camera inputs to record with
#if unsure of camera inputs, use 'detect' to see a list of detected cameras and inputs
task = 'record' 
cam_inputs = [1,2] #enter inputs as [input1, input2] i.e. [1,2,3,4]


if rotation_input and not len(cam_inputs) == len(rotation_input):
    raise ValueError('The number of camera inputs and rotation inputs does not match')
if not rotation_input:
    rotation_input = [None]*len(cam_inputs)
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
    for x,y in zip(cam_inputs,rotation_input):
        u = webcam.VideoSetup(x,paramDict,y)
        u.start()
        ulist.append(u)
        
    for k in ulist:
        k.join()

#-----------------------------------------------RECORD
#Press ESCAPE to stop the recording process, and continue onto the time-syncing/editing process

elif task == 'record':#don't change this boolean by accident pls
    recordPath = filepath/sessionID
    recordPath.mkdir(exist_ok='True')
    is_empty = not any(recordPath.iterdir())
    if not is_empty:
            raise RuntimeError(sessionID + ' folder already contains files. check session ID')

    if not cam_inputs:
        raise ValueError('Camera input list (cam_inputs) is empty')
    table = webcam.RunCams(cam_inputs,recordPath,sessionID,paramDict,rotation_input) #press ESCAPE to end the recording
    
elif not task:
    print('No task detected')


elif task == 'debug':
    recordPath = filepath/sessionID
    webcam.DebugTime(sessionID,recordPath)

    
else:
    print('Unrecognized task: please enter task as "detect","setup",or "record"')
