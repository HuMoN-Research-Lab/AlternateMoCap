%% Master Timeline
%this section uses creates a master timeline and time-syncs all four cameras to the master timeline. 

[c1,c2,c3,c4] = csvread('four_test_2.csv');
%use CSV input to create separate of timestamps for each camera

[time2,frame2,perc2] = mastersync2(9,50,c1,c2,c3,c4);

perc2