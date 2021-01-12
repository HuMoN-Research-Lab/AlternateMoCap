# -*- coding: utf-8 -*-
"""
Created on Mon Nov  9 13:07:36 2020

@author: Rontc
"""

def mastersync(filename):    
    import pandas as pd
    import numpy as np

    def closeNeighb(camera,point):
        idx = (np.abs(camera - point)).argmin() 
        return idx
    
    df = pd.read_csv (filename)
    #print (df)
    
    arr = df.to_numpy()
    #print(arr)
    
   
        
    cam1 = arr[0,1:]
    
    cam2 = arr[1,1:]
    
    cam3 = arr[2,1:]
    
    cam4 = arr[3,1:]
    
    begin = np.ceil(min(cam1[0],cam2[0],cam3[0],cam4[0]))
    end = np.floor(np.nanmax([cam1[-1],cam2[-1],cam3[-1],cam4[-1]]))
    print('end',cam1[-1],cam2[-1],cam3[-1],cam4[-1])
    print('test',begin,end)    
    #camera = arr[:,1:]
    camera = [cam1,cam2,cam3,cam4]
    #print(camera)
        
    #begin = 9
    #end = 50
    rate_arr= []
    
    cam_names = ["Cam A","Cam B","Cam C","Cam D"]
    n = 0;
    for x in camera:
      ss = closeNeighb(x,begin)
      es = closeNeighb(x,end)
      print("using frames:", ss,"-",es,"for",cam_names[n])
      n +=1
      int = x[ss:es]
      test = np.mean(np.diff(int))
      rate_arr.append(test)
    
    intvl = np.mean(rate_arr)
    mt = np.arange(begin,end,intvl)
    ctest = [cam1]
    
    si = [];
    framelist = mt
    timelist = mt
    idx_start = closeNeighb(cam1,mt[0])
    idx_end = closeNeighb(cam1,mt[-1])
    del_num= [];
    buf_num= [];
    buf_per_list = [];
    del_per_list = [];
    #framelist = [];
    count = 0
    n = 0;
    for y in camera:
        si = [];
        sf =[];
    
        count += 1
        #idx_start = closeNeighb(y,mt[0])
        #idx_end = closeNeighb(y,mt[-1])
        #print(idx_start)
        #cam_new = x[idx_start:idx_end]
        for z in mt:
            si_pt = closeNeighb(y, z)
            si.append(si_pt)
            sf = y[si]
            
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
    col_list = ['Master Timeline','CamA','CamB','CamC','CamD']
    frameTable.columns = col_list
    timeTable = pd.DataFrame(timelist)
    timeTable.columns = col_list
    framerate = 1/intvl
    results = {'Cam':['CamA','CamB','CamC','CamD'],'#Del':del_num,'%Del':del_per_list,'#Buf':buf_num,'%Buf':buf_per_list}
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

#n_cam= 4
#camNum = range(n_cam)
#g,h,j,k = mastersync('test8_12_1.csv')