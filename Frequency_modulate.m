clc
clear
%% import data
% change location1, obtain all ABF file in a directory in one time and frequency modulate
% example："G:/TW/实验数据/**/*.abf", obtain all ABF file in the G:/TW/实验数据/.
namelist = dir("G:\TW\实验数据\455 33纯样\20230419_02-09_WT_455 C5-4M_100#\20230419_02_D/**/*.abf"); % change location 1
namelist = transpose(struct2cell( namelist));
[namerow,namecolumn] = size(namelist);
for i = 1:namerow
    subpath =  namelist{i,2};
    strlen = strlength(subpath);
    subpath = insertAfter(subpath,strlen,"\");
    subname = namelist{i,1};
    abf = [subpath,subname];
    [d,si,h]=abfload2(abf,'start',0,'stop','e');
    fs = 19531;
    xbData = wdenoise(d,5,DenoisingMethod = "Bayes",Wavelet="sym4",ThresholdRule = "soft",NoiseEstimate = "LevelDependent");
    [xlowData_1,d1] = lowpass(d,50,fs);
    [xlowData_2,d2] = lowpass(d,100,fs);
    [xlowData_3,d3] = lowpass(d,200,fs);
    [xlowData_4,d4] = lowpass(d,500,fs);
    xb = xbData(:,1);
    xlow_1 = xlowData_1(:,1);
    xlow_2 = xlowData_2(:,1);
    xlow_3 = xlowData_3(:,1);
    xlow_4 = xlowData_4(:,1);
    subname(end-3:end) = [];
    frquency_wavelet = strcat(subpath,subname,"_wavelet.mat");
    frquency_50 = strcat(subpath,subname,"_50.mat");
    frquency_100 = strcat(subpath,subname,"_100.mat");
    frquency_200 = strcat(subpath,subname,"_200.mat");
    frquency_500 = strcat(subpath,subname,"_500.mat");
    save(frquency_wavelet,"xb");
    save(frquency_50,"xlow_1");
    save(frquency_100,"xlow_2");
    save(frquency_200,"xlow_3");
    save(frquency_500,"xlow_4");
    fprintf("Processing........ %f",(i/namerow)*100);
end































