# -*- coding: utf-8 -*-
"""
Created on Mon Nov  9 13:07:36 2020

@author: Rontc
"""

def mastersync(filename,camNum):    
    import pandas as pd
    import numpy as np

    def closeNeighb(camera,point):
        idx = (np.abs(camera - point)).argmin() 
        return idx
    
    df = pd.read_csv (filename)
    #print (df)
    
    arr = df.to_numpy()
    #print(arr)
    stampList = []
    beginList =[]
    endList = []
    for x in camNum:
        cam = arr[x,1:]
        start = cam[0]
        #print(begin)
       
        stop_pt = -1
        stop = cam[stop_pt]
        while np.isnan(stop):
            stop_pt -= 1
            stop = cam[stop_pt]
            
            
        stampList.append(cam)
        beginList.append(start)
        endList.append(stop)

    
    #print(beginList)
    
    begin = np.ceil(max(beginList))
    end = np.floor(min(endList))
    print('end',endList)
    print('test',begin,end)    

    #camera = [cam1,cam2,cam3,cam4]
    
    rate_arr= []
    cam_names = []
    for x in camNum:
      ids = 'Cam{}'.format(x+1)
      cam_names.append(ids)
  
    n = 0;
    for x in camNum:
      current_cam = stampList[x]
      ss = closeNeighb(current_cam,begin)
      es = closeNeighb(current_cam,end)
      print("using frames:", ss,"-",es,"for",cam_names[n])
      n +=1
      intl = current_cam[ss:es]
      test = np.mean(np.diff(intl))
      rate_arr.append(test)
    
    intvl = np.mean(rate_arr)
    mt = np.arange(begin,end,intvl)
   
   
    si = [];
    framelist = mt
    timelist = mt
 
    del_num= [];
    buf_num= [];
    buf_per_list = [];
    del_per_list = [];
    #framelist = [];
    count = 0
    n = 0;

    for y in camNum:
        this_cam = stampList[y]
        si = [];
        sf =[];
    
        count += 1
        #idx_start = closeNeighb(y,mt[0])
        #idx_end = closeNeighb(y,mt[-1])
        #print(idx_start)
        #cam_new = x[idx_start:idx_end]
        for z in mt:
            si_pt = closeNeighb(this_cam, z)
            si.append(si_pt)
            sf = this_cam[si]
            
        print("starting detection:",cam_names[n])
        framelist = np.column_stack((framelist,si))
        timelist = np.column_stack((timelist,sf))
    
        buf_count = 0;
        del_count = 0;
     
        
        for i in range(0,len(si)-1):
            dis = si[i+1] - si[i]
            if dis == 1:
                None
            elif dis == 0:
                buf_count += 1
                #print("Buffer")
                frame1 = abs(mt[i]-sf[i])
                frame2 = abs(mt[i+1]-sf[i])
                if frame1>frame2:
                 framelist[i,count] = -1
                 timelist[i,count] = -1
                else:
                 framelist[i+1,count] = -1;
                 timelist[i+1,count] = -1;
            elif dis > 1:
               del_count += 1
            else:
                
                print("something else happened")
        del_num.append(round(del_count,1))
        buf_num.append(round(buf_count,1))
        print(buf_count,len(framelist))
        buf_per = (buf_count/len(framelist))*100
        del_per = (del_count/len(framelist))*100
        buf_per_list.append(round(buf_per,2))
        del_per_list.append(round(del_per,2))
       
        print(del_num,buf_num,buf_per_list,del_per_list)
        print("deleted frames:",del_count)
        print("buffered frames:",buf_count)
        n +=1
        
        
    frameTable = pd.DataFrame(framelist)   
    col_list = ['Master Timeline'] + cam_names
    frameTable.columns = col_list
    timeTable = pd.DataFrame(timelist)
    timeTable.columns = col_list
    framerate = 1/intvl
    results = {'Cam':cam_names,'#Del':del_num,'%Del':del_per_list,'#Buf':buf_num,'%Buf':buf_per_list}
    res_d = pd.DataFrame(results,columns = ['Cam','#Del','%Del','#Buf','%Buf'])
    #print(frameTable,timeTable)
    return frameTable,timeTable,framerate,res_d
 
    
    
    """
    from sklearn.neighbors import NearestNeighbors
    
    neigh = NearestNeighbors(n_neighbors=1)
    
    neigh.fit(cam1)
    neigh.kneighbors(cam2, 1, return_distance=False)
    #neigh.fit([cam1,cam2,cam3,cam4])
    #print(chck)
    
    """

n_cam= 4
camNum = range(n_cam)
u,i,o,p = mastersync('test9_12_1.csv',camNum)