
%% This script is used for add label for each analyte
% you need import calibrated data first
% example: ResultCorrect2OHS is the data i import
ResultCorrect2OHS = removevars(ResultCorrect2OHS, {'logDwellTime_1','logDwellTime_2','logDwellTime_3','logDwellTime_4','logDwellTime_5'});
[numRows_1,numCols_1] = size(ResultCorrect2OHS);
ResultCorrect2OHS = table2array(ResultCorrect2OHS);
% S45S is the difference between mean value of many parallel experiment and mean value of ResultCorrect2OHS, if you don't
% have,please add % before line 10-13
S455 = table2array(standard(8,1:43));
for i = 1:43
    ResultCorrect2OHS(:,i) = (ResultCorrect2OHS(:,i)+S455(1,i));
end
ResultCorrect2OHS = array2table(ResultCorrect2OHS, "VariableNames",[  "Blockade" "std" ...
    "peak" "FWHM" "max-min"  "Skewness" "Kurtosis" "log(Dwell time)" "Blockade_1" "std_1" ...
    "peak_1" "FWHM_1" "max-min_1"  "Skewness_1" "Kurtosis_1"  "Blockade_2" "std_2" ...
    "peak_2" "FWHM_2" "max-min_2"  "Skewness_2" "Kurtosis_2" "Blockade_3" "std_3" ...
    "peak_3" "FWHM_3" "max-min_3"  "Skewness_3" "Kurtosis_3"  "Blockade_4" "std_4" ...
    "peak_4" "FWHM_4" "max-min_4"  "Skewness_4" "Kurtosis_4"  "Blockade_5" "std_5" ...
    "peak_5" "FWHM_5" "max-min_5"  "Skewness_5" "Kurtosis_5"]);
% change location, "2OH_S"——the label of my data, you can change according
% your own requiement
ResultCorrect2OHS(:,numCols_1+1) ={'2OH_S'};
ResultCorrect2OHS.Properties.VariableNames{numCols_1+1} = 'label';


