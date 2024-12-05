
import numpy as np
import pandas as pd
# from fitter import Fitter
import scipy as sp
import Function as F

dataSequence = pd.read_excel("G:/TW_CMY_数据/DATASequence.xlsx", sheet_name="Sheet2")  # change location 1, the lcoation of DataSequenc.xlsx in your laptop
dataSequence = np.array(dataSequence).astype(str)
numData = dataSequence.shape[0]
dealResult = []
fitdataName =[]
datasize = []
fitdata_non = []
fitdata = []
for d in  range(40,numData):
    try:
        path = dataSequence[d, 0]
        print(path)
        data_target = pd.read_excel(path + "Result_1.xlsx", sheet_name=dataSequence[d, 2])
        data_targetColumn = data_target.columns
        for name in data_targetColumn:
            if name == "totalBasline_0":
                data_target = data_target.drop("totalBasline_0", axis=1)
                data_targetColumn = data_targetColumn.drop(["totalBasline_0"])
                break
        data_targetColumn = data_targetColumn.drop(["Unnamed: 0"])
        data_target = np.array(data_target)
        data_Is = pd.read_excel(path + "Result_1.xlsx", sheet_name=dataSequence[d, 1])
        data_IsColumn = data_Is.columns
        for name in data_IsColumn:
            if name == "totalBasline_0":
                data_Is = data_Is.drop("totalBasline_0", axis=1)
                break
        data_Is = np.array(data_Is)
        writer_1 = pd.ExcelWriter(path + "Result_Correct.xlsx")
        columns = data_Is.shape[1]  # 列数
        numRows_Is = data_Is.shape[0]  # 行数
        numRows = data_target.shape[0]
        result = np.empty([numRows, columns-1])
        result_Is = np.empty([6, columns - 1])
        result[:, 0] = data_target[:, 1]
        result_Is[:, 0] = 0
        ## 数据统计
        for i in range(2, columns):
            if i == 16:
                bins = 90
                threshold = 0.2
                print(data_targetColumn[i - 1])
            else:
                bins = 30
                threshold = 0.01
            data = data_Is[:, i]
            if (((i - 2) % 8 == 0) | ((i - 2) % 8 == 7) ):
                mean_Is, std_Is, g_Is = F.gaussFit_2(data, bins, data_targetColumn[i - 1], "IS", path)
            elif ((i-2) % 8 == 5):
                data = data_Is[:, i]
                numRows = data.shape[0]
                data = np.sort(data, axis=0)[::-1]
                deletedata = int(np.floor(numRows * threshold))
                deletedatadown = np.linspace(0, int(np.floor(deletedata / 2)) - 1, int(deletedata / 2)).astype(int)
                deletedataup = -1 * deletedatadown
                data_new = np.delete(data, deletedatadown, axis=0)
                data_new = np.delete(data_new, deletedataup, axis=0)
                mean_Is, std_Is, g_Is = F.gaussFit_2(data_new, bins, data_targetColumn[i - 1], "IS", path)
            else:
                data = data_Is[:, i]
                numRows = data.shape[0]
                data = np.sort(data, axis=0)[::-1]
                deletedata = int(np.floor(numRows * threshold))
                deletedatanum = np.linspace(0, deletedata - 1, deletedata).astype(int)
                data_new = np.delete(data, deletedatanum, axis=0)
                mean_Is, std_Is, g_Is = F.gaussFit_2(data_new, bins, data_targetColumn[i - 1], "IS", path)

            # print(mean_Is)
            # print(std_Is)
            result_Is[0, i - 1] = mean_Is.value
            result_Is[1, i - 1] = std_Is.value
            result[:, i - 1] = data_target[:, i] / mean_Is.value
        for i in range(2, columns):
            if i == 16:
                bins = 90
                threshold = 0.03
                print(data_targetColumn[i - 1])
            else:
                bins = 30
                threshold = 0.01
            data = data_target[:, i]
            if (((i - 2) % 8 == 0) | ((i - 2) % 8 == 7)):
                mean_Is, std_Is, g_Is = F.gaussFit_2(data, bins, data_targetColumn[i - 1], "IS", path)
            elif ((i - 2) % 8 == 5):
                data = data_target[:, i]
                numRows = data.shape[0]
                data = np.sort(data, axis=0)[::-1]
                deletedata = int(np.floor(numRows * threshold))
                deletedatadown = np.linspace(0, int(np.floor(deletedata / 2)) - 1, int(deletedata / 2)).astype(int)
                deletedataup = -1 * deletedatadown
                data_new = np.delete(data, deletedatadown, axis=0)
                data_new = np.delete(data_new, deletedataup, axis=0)
                mean_Is, std_Is, g_Is = F.gaussFit_2(data_new, bins, data_targetColumn[i - 1], "IS", path)
            else:
                data = data_target[:, i]
                numRows = data.shape[0]
                data = np.sort(data, axis=0)[::-1]
                deletedata = int(np.floor(numRows * threshold))
                deletedatanum = np.linspace(0, deletedata - 1, deletedata).astype(int)
                data_new = np.delete(data, deletedatanum, axis=0)
                mean_Is, std_Is, g_Is = F.gaussFit_2(data_new, bins, data_targetColumn[i - 1], "IS", path)
            result_Is[2, i - 1] = mean_Is.value
            result_Is[3, i - 1] = std_Is.value

        deleteRow = []
        for i in range(columns-1):
            if (((i %8) == 3) |((i %8) == 4)|((i %8) == 7)):
                threhold = 0.002
                data = result[:, i]
                numRows = result.shape[0]
                datasort = np.argsort(data, axis=0)[::-1]
                deletedata = int(np.floor(numRows * threhold))
                for m in range(deletedata):
                    deleteRow.append(datasort[m])
        deleteSigleRow = np.unique(np.array(deleteRow))
        result = np.delete(result,deleteSigleRow,axis=0)

        for i in range(columns - 2):
            data = result[:, i + 1]
            if (((i) % 8 == 0) | ((i) % 8 == 7) | ((i) % 8 == 5)):
                mean_Is, std_Is, g_Is = F.gaussFit_2(data, 90, data_targetColumn[i + 1], "IS", path)
                result_Is[4, i + 1] = mean_Is.value
                result_Is[5, i + 1] = std_Is.value
            else:
                numRows = data.shape[0]
                data = np.sort(data, axis=0)[::-1]
                deletedata = int(np.floor(numRows * 0.01))
                deletedatanum = np.linspace(0, deletedata - 1, deletedata).astype(int)
                data = np.delete(data, deletedatanum, axis=0)
                mean_Is, std_Is, g_Is = F.gaussFit_2(data, 50, data_targetColumn[i + 1], "IS", path)
                result_Is[4, i + 1] = mean_Is.value
                result_Is[5, i + 1] = std_Is.value

        fitdata_non.append(result_Is[2, 1:columns])
        fitdata_non.append(result_Is[3, 1:columns])
        fitdata.append(result_Is[4, 1:columns])
        fitdata.append(result_Is[5, 1:columns])
        datasize.append(result.shape[0])
        datasize.append(result.shape[0])
        fitdataName.append(path)
        fitdataName.append(path)
        Result = pd.DataFrame(result, columns=data_targetColumn)
        Result = Result.drop("Level_0", axis=1)
        Result.to_excel(writer_1, sheet_name='Result_I1')
        Result_Is = pd.DataFrame(result_Is, columns=data_targetColumn)
        Result_Is = Result_Is.drop("Level_0", axis=1)
        Result_Is.to_excel(writer_1, sheet_name='FitData')
        writer_1._save()
        writer_1.close()
        print("ok")
    except Exception as err:
        print(err)
        continue

writer_2 = pd.ExcelWriter(dataSequence[0, 0] + "Result_fit_1.xlsx")
fitdataName = np.array(fitdataName).reshape([-1,1])
datasize = pd.DataFrame(np.array(datasize).reshape([-1,1]))
fitdata = np.array(fitdata)
fitdata_non = np.array(fitdata_non)
fit_non = pd.DataFrame(np.concatenate((fitdataName,fitdata_non),axis=1))
fit = pd.DataFrame(np.concatenate((fitdataName,fitdata),axis=1))
fit_non.to_excel(writer_2,sheet_name="fit_non")
fit.to_excel(writer_2,sheet_name="fit")
datasize.to_excel(writer_2,sheet_name="datasize")
writer_2._save()
writer_2.close()

