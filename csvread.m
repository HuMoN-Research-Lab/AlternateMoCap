function [c1,c2,c3,c4] = csvread(x)

list = readtable(x);
list_edit = list(2:5,2:end);
c1 = table2array(list_edit(1,:));
c2 = table2array(list_edit(2,:));
c3 = table2array(list_edit(3,:));
c4 = table2array(list_edit(4,:));

end