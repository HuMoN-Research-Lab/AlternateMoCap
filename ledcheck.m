

cam1time = table2array(test31231(2,1:2922))
cam2time = table2array(test31231(3,1:2922))
cam3time = table2array(test31231(4,1:2922))
cam4time = table2array(test31231(5,1:2922))

cam1tedit = cam1time(12:2911);
cam2tedit = cam2time(12:2911);
cam3tedit = cam3time(12:2911);
cam4tedit = cam4time(13:2912);

%%
data = csvread('unedit_test3_12_29.csv');

framelist = data(1,1:2922);
cam1 = data(2,1:2922);
cam2 = data(3,1:2922);
cam3 = data(4,1:2922);

cam4 = data(5,1:2922);

%%
data2 = csvread('edit_test3_12_29.csv');
framelist2 = data2(1,:);
cam1_2 = data2(2,:);
cam2_2 = data2(3,:);
cam3_2 = data2(4,:);

cam4_2 = data2(5,:);


%%
% clear all
  %plot(framelist,cam1)
%  hold on
% plot(framelist,cam2)
%  plot(framelist,cam3)

[c1p1,c1loc] = findpeaks(cam1,'MinPeakDistance',30,'MinPeakHeight',10)
[c2p1,c2loc] = findpeaks(cam2,'MinPeakDistance',2,'MinPeakHeight',12)
[c3p1,c3loc] = findpeaks(cam3,'MinPeakDistance',2,'MinPeakHeight',18)
[c4p1,c4loc] = findpeaks(cam4,'MinPeakDistance',2,'MinPeakHeight',12)
% scatter(c3_l,c3_p)

[c1p2,c1loc2] = findpeaks(cam1_2,'MinPeakDistance',30,'MinPeakHeight',10)
[c2p2,c2loc2] = findpeaks(cam2_2,'MinPeakDistance',2,'MinPeakHeight',15)
[c3p2,c3loc2] = findpeaks(cam3_2,'MinPeakDistance',2,'MinPeakHeight',18)
[c4p2,c4loc2] = findpeaks(cam4_2,'MinPeakDistance',2,'MinPeakHeight',12)

close all
% plot(framelist2,cam4_2)
% hold on
% scatter(c4loc2,c4p2)

% c4loc= [c4loc 2923]


%%
plot(framelist,cam4)
hold on
scatter(c2_l,c2_p)
%%
%%
diff1 = c2loc - c1loc;
diff2 = c3loc - c1loc;
diff3 = c4loc - c1loc;

diff1_2 = c2loc2 - c1loc2;
diff2_2 = c3loc2 - c1loc2;
diff3_2 = c4loc2 - c1loc2;

%%
timediff1 = cam2time(c2loc) - cam1time(c1loc);
timediff2 = cam3time(c3loc) - cam1time(c1loc);
timediff3 = cam4time(c4loc) - cam1time(c1loc);

timediff1_2 = cam2tedit(c2loc2) - cam1tedit(c1loc2);
timediff2_2 = cam3tedit(c3loc2) - cam1tedit(c1loc2);
timediff3_2 = cam4tedit(c4loc2) - cam1tedit(c1loc2);
% diff3 = c3_l - c2_l
%%
 close all
 
subplot(321)
plot(framelist,cam1)
hold on
plot(framelist,cam2)
plot(framelist,cam3)
plot(framelist,cam4)
legend('cam1','cam2','cam3','cam4','Location','BestOutside')
title('Raw Video Brightness/Camera')
xlabel('Frames')
ylabel('Brightness')
% ylim([-2,20])

subplot(322)
plot(framelist2,cam1_2)
hold on
plot(framelist2,cam2_2)
plot(framelist2,cam3_2)
plot(framelist2,cam4_2)
legend('cam1','cam2','cam3','cam4','Location','BestOutside')
title('Synced Video Brightness/Camera')
xlabel('Frames')
ylabel('Brightness')
ylim([-10,30])

subplot(323)

bins = -4:1:4;
histogram(diff1,bins,'Normalization','probability','DisplayName','Cam2')
 hold on
histogram(diff2,bins,'Normalization','probability','DisplayName','Cam3')
histogram(diff3,bins,'Normalization','probability','DisplayName','Cam4')
l1 = legend;
l1.Location = 'northwest';
xlabel('Frame Delay from Camera 1')
ylabel('Normalized Frequency')
title('Raw Video Frame Delays')


subplot(324)
% close all
bins = -4:1:4;
histogram(diff1_2,bins,'Normalization','probability','DisplayName','Cam2')
 hold on
histogram(diff2_2,bins,'Normalization','probability','DisplayName','Cam3')
histogram(diff3_2,bins,'Normalization','probability','DisplayName','Cam4')
l1 = legend;
l1.Location = 'northwest';
xlabel('Frame Delay')
xlabel('Frame Delay from Camera 1')
ylabel('Normalized Frequency')
title('Synced Video Frame Delays')

subplot(325)
% close all
bins = -4:.5:4;
histogram(timediff1*100,bins,'Normalization','probability','DisplayName','Cam2')
 hold on
histogram(timediff2*100,bins,'Normalization','probability','DisplayName','Cam3')
histogram(timediff3*100,bins,'Normalization','probability','DisplayName','Cam4')
l1 = legend;
l1.Location = 'northwest';
xlabel('Time Delay')
xlabel('Time Delay from Camera 1 (ms)')
ylabel('Normalized Frequency')
title('Raw Video Time Delays')  

subplot(326)
% close all
bins = -4:.5:4;
histogram(timediff1_2*100,bins,'Normalization','probability','DisplayName','Cam2')
 hold on
histogram(timediff2_2*100,bins,'Normalization','probability','DisplayName','Cam3')
histogram(timediff3_2*100,bins,'Normalization','probability','DisplayName','Cam4')
l1 = legend;
l1.Location = 'northwest';
xlabel('Time Delay')
xlabel('Time Delay from Camera 1 (ms)')
ylabel('Normalized Frequency')
title('Synced Video Time Delays')


%%
scatter(c1_l,c1_p)
hold on 
scatter(c2_l,c2_p)
scatter(c3_l,c3_p)
%%
close all
scatter(c3_l,c3_p)
hold on
scatter(c1_l,c1_p)