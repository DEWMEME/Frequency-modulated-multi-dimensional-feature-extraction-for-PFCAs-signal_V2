
%% 选择用于训练的数据，输入类型为table
function [t,p] = selectData(size1,size2, selectFeatures)
fprintf("importing Data.....\n");
data = load("/home/zx/LHS/cFtdata_2400.mat");  % change the location to your own data
names = fieldnames(data);
t= table();
p = table();
if isempty(selectFeatures)==1
    selectF = linspace(1,44,44);
else
    selectF = selectFeatures;
end
for i= 1:length(names)
    index = names(i);
    data_name = strcat('data.',index);
    perdata = eval(data_name{1}) ;
    [cf1,cf2] = size(perdata);
    R_1 = randperm(cf1,size1);
    t = [t;perdata(R_1,selectF)];
    perdata(R_1,:) = [];
    R_2 = randperm(cf1-size1,size2);
    p = [p;perdata(R_2,selectF)];
end




