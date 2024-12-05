
clc
clear
% change location 1: the ABF file location you need process
% example: G:\CMY\5/**/ , it means i will obtain all folder under
% G:\CMY\5/**/, including itself
namelist = dir("G:\CMY\5/**/"); 
% change location 2: path = the value before ** of namelist 
path = "G:\CMY\5/";
namelist_wavelet = dir(path+"/**/*_wavelet.mat");
namelist_50 = dir(path+"/**/*_50.mat"); 
namelist_100 = dir(path+"/**/*_100.mat"); 
namelist_200 = dir(path+"/**/*_200.mat"); 
namelist_500 = dir(path+"/**/*_500.mat"); 
namelist_xlsx = dir(path+"/**/*.xlsx"); 
namelist_abf = dir(path+"/**/*.abf"); 
namelist = transpose(struct2cell( namelist));
namelist_wavelet = transpose(struct2cell( namelist_wavelet));
namelist_50 = transpose(struct2cell( namelist_50));
namelist_100 = transpose(struct2cell( namelist_100));
namelist_200 = transpose(struct2cell( namelist_200));
namelist_500 = transpose(struct2cell( namelist_500));
namelist_xlsx = transpose(struct2cell( namelist_xlsx));
namelist_abf = transpose(struct2cell( namelist_abf));
folder = unique(namelist(:,2));
% run here and pause
% delete the extra value in the foler if folder, namelist_xlsx,
% namelist_abf, name_wavelet, namelist_50, namelist_100,
% namelist_200,namelist_500 have different size.
datasequence = [folder,namelist_xlsx(:,1),namelist_abf(:,1),namelist_wavelet(:,1) namelist_50(:,1),namelist_100(:,1),namelist_200(:,1),namelist_500(:,1)];
[numrow,numcol] =size(datasequence);
for i  =1:numrow
    for j = 1:8       
        namelist_wa(i,j) = strrep(datasequence(i,j),"'","");
    end
end
for i = 1:numrow
    namelist_wa(i,1) = strrep(namelist_wa(i,1),"\","/");
    namelist_wa(i,1) = append(namelist_wa(i,1),"/");
end
colnumname = {'folder','xlsx','abf','wavelet','F50','F100','F200','F500'};
namelist_wa = [colnumname;namelist_wa];
writematrix(namelist_wa,"Datasequence.xlsx",Sheet="Sheet1")
    






