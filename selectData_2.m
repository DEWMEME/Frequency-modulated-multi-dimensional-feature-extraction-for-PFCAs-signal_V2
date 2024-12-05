function [t,features] = selectData_2(size1,size2,size3,selectFeatures)
fprintf("importing Data.....\n");
data = load("/home/zx/LHS/FTCA_C6_9000.mat");   % change the location to your own data
names = fieldnames(data);
t= table();
if isempty(selectFeatures)==1
    selectF = linspace(1,44,44);
else
    selectF = selectFeatures;
end
for i= 1:length(names)
    index = names(i);
    data_name = strcat('data.',index);
    perdata = eval(data_name{1}) ;
    if index == "FTCAC3" 
        [cf1,cf2] = size(perdata);
        R_1 = randperm(cf1,size1);
        t = [t;perdata(R_1,selectF)];
    elseif index == "C6C6"
        [cf1,cf2] = size(perdata);
        R_2 = randperm(cf1,size2);
        t = [t;perdata(R_2,selectF)];
    elseif index == "C5C6"
        [cf1,cf2] = size(perdata);
        R_3 = randperm(cf1,size3);
        t = [t;perdata(R_3,selectF)];
    else
        continue
    end
end
features = perdata.Properties.VariableNames;




