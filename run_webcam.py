# -*- coding: utf-8 -*-
"""
Created on Mon Dec  7 14:16:45 2020

@author: Rontc
"""

import webcam 

n_cam= 4 #number of webcams being used
iCam = [1,2,3,4] #the USB input for each camera that you're using 
path = r'C:\Users\Rontc\Documents\GitHub\AlternateMoCap\\' #add your file path to save a CSV as r'filepath\', and for right now **include a second backslash at the end of your path**
sessionName = 'test5_12_7' #create a filename for the output CSV

webcam.runCams(n_cam,iCam,path,sessionName) #press ESCAPE to end the recording
