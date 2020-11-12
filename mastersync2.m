function [timeTable, frameTable,percTable] = mastersync2(bs,es,a,b,c,d)
    camera = [a;b;c;d];
    intl = [];
    for k = 1:size(camera,1)
        cam0 = camera(k,:);
        sf = knnsearch(cam0',bs); %find the frame closest to the interval start time
        ef = knnsearch(cam0',es); %find the frame closest to the interval end time
        int = cam0(sf:ef); %create an array of all timestamps in that one second interval
        intl = [intl mean(diff(int))];
    end
     frame_time = mean(intl);
     mt = [bs:frame_time:es];

   timelist = [mt']; %create an array for all camera time stamps
   framelist= [mt'];%create an array for all camera frames
  del_list = []; %to store deletion percentage for each camera
   buf_list = []; %to store buffer percentage for each camera
   del_num = []; %to store number of frames deleted for each camera
   buf_num = []; %to store number of buffer frames added for each camera
for j = 1:size(camera,1) %iterate through the timestamps for each camera
   cam = camera(j,:); 
   %find the closest start and endpoints to the master timeline, create a 
   %timeline within that interval 
   %idx_start = knnsearch(cam',mt(1));
   %idx_end = knnsearch(cam',mt(end));
   %cam_new = [cam(idx_start:idx_end)];
   %use KNN search to find the closest indices (which is the same as the frames we
   %need), and then get the timestamps that we need
   si = knnsearch(cam',mt');
   sf = cam(si);

  
   timelist(:,j+1) = sf;%add the timestamps for this camera to the array
   framelist(:,j+1) = si; %add the frames needed for this camera to the array
   del_count = 0; %deletion counter
   buf_count = 0; %buffer counter
   fprintf(" <strong> Starting detection </strong> \n")
   %use to detect where buffered and deleted frames occur. Modify the
   %frame/timelist to replace buffer frames with a 0
   for i = 1:length(si)-1
    dis = si(i+1) - si(i); %look for the distance between each pair of points
    if dis == 1 %if the distance is one, they are consecutive frames. all good
    elseif dis == 0% if 0, then we have a repeated/buffer frame
            fprintf("buffer, %d \n",si(i))
            buf_count = buf_count +1;
            %find the distance between the buffer frames to the two
            %timestamps it's associated with. The frame with the further
            %distance is the buffer frame. change it's associated position
            %in framelist and timelist to 0
            frame1 = abs(mt(i)-sf(i));
            frame2 = abs(mt(i+1)-sf(i));
            
            if frame1 > frame2
                 framelist(i,j+1) = 0;
                   timelist(i,j+1) = 0;
            else
                framelist(i+1,j+1) = 0;
                   timelist(i+1,j+1) = 0;
            end
            
    elseif dis > 1 %a frame was deleted
         fprintf("deletion, %d \n",si(i)+1)
         del_count = del_count + 1;
    else %a catch-all for scenarios I might not have thought of
        fprintf("something else happened at frame %d \n",i) 
    end

   end


%add to the count for each camera, calculate percentages, and create a list
%of percentages for each camera
del_num = [del_num del_count];
buf_num = [buf_num buf_count];
del_per = (del_count/length(si))*100;
buf_per = (buf_count/length(si))*100;
%fprintf("Deletion percentage: %1.1f percent  \n", del_per)
%fprintf("Buffer percentage: %1.1f percent  \n", buf_per)
del_list = [del_list del_per];
buf_list = [buf_list buf_per];



end
colNames = {'masterTimeline','camA','camB','camC','camD'};
frameTable = array2table(framelist,'VariableNames',colNames);
timeTable = array2table(timelist,'VariableNames',colNames);

colNames2 = {'camA','camB','camC','camD'};
rowNames = {'Frames Deleted','Deletion Percentage','Frames Buffered','Buffer Percentage'};
percTable = array2table([del_num;del_list;buf_num;buf_list],'RowNames',rowNames,'VariableNames',colNames2);

frame_time
end

