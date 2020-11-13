# -*- coding: utf-8 -*-
"""
Created on Tue Oct 20 16:05:04 2020

@author: Rontc
"""
import cv2 as cv 

def testDevice(source):
   cap = cv.VideoCapture(source,cv.CAP_DSHOW) 
   #if cap is None or not cap.isOpened():
       #print('Warning: unable to open video source: ', source)
   if cap.isOpened():
        print('Opened: ',source)
        cap.release()
        cv.destroyAllWindows() 
       
for x in range(10):        
   testDevice(x)
    