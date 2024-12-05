import numpy as np
import pyabf
import pandas as pd
from seaborn.external.kde import gaussian_kde
import Function as te
from scipy.io import loadmat
from joblib import Parallel,delayed
import matplotlib.pyplot as plt
import seaborn as sns

dataSequence = pd.read_excel("G:/TW_CMY_数据/DATASequence.xlsx",sheet_name="Sheet1")  # change location 1, the lcoation of DataSequenc.xlsx in your laptop
dataSequence = np.array(dataSequence).astype(str)
numData = dataSequence.shape[0]
dealResult = []
for d in range(numData):
    try:
        path = dataSequence[d,0]
        # Result save location
        writer = pd.ExcelWriter(path+"Result.xlsx")
        writer_2 = pd.ExcelWriter(path + "Result_1.xlsx")
        abf = pyabf.ABF(path+dataSequence[d,2])
        print(abf)
        abf.setSweep(0)
        intervalTime = float("{:.7f}".format(1 / abf.sampleRate))
        X = np.arange(len(abf.sweepY)) * intervalTime * 1000
        Y = np.array(abf.sweepY)
        Y_wavelet = loadmat(path+dataSequence[d,3],mat_dtype = True)
        Y_xlow_1 = loadmat(path+dataSequence[d,4],mat_dtype = True)
        Y_xlow_2 = loadmat(path+dataSequence[d,5],mat_dtype = True)
        Y_xlow_3 = loadmat(path+dataSequence[d,6],mat_dtype = True)
        Y_xlow_4 = loadmat(path+dataSequence[d,7],mat_dtype = True)
        Y_xbData = Y_wavelet['xb'][:,0]
        Y_xlowdata_1 = Y_xlow_1['xlow_1'][:,0]
        Y_xlowdata_2  = Y_xlow_2['xlow_2'][:,0]
        Y_xlowdata_3  = Y_xlow_3['xlow_3'][:,0]
        Y_xlowdata_4  = Y_xlow_4['xlow_4'][:,0]
        numRows = X.shape[0]

        allData = pd.read_excel(path+dataSequence[d,1], 'FULL')
        allData = np.array(allData)
        dataNum = allData.shape[0]
        deletRow = []
        for i in range(dataNum):
            if allData[i,0] == 0:
                break
            deletRow.append(i)
        for j in reversed(range(dataNum)):
            if allData[j,0] ==0:
                break
            deletRow.append(j)
        if len(deletRow) != 0 :
            allData = np.delete(allData,deletRow,axis=0)
        leve1 = np.argwhere(allData[:,0] == 1)
        clampfitData = allData[leve1,[2,3]]
        cBaselineRefer = allData[:,[0,2,3]]
        standardData = pd.read_excel(path+dataSequence[d,1], sheet_name='Background')
        totalBaseline = standardData['Line'][1]
        Y_Blocakade = (totalBaseline - Y_xbData) * 100 / totalBaseline
        clampfitNumRows = clampfitData.shape[0]
        output = np.empty([clampfitNumRows, 13])

        # constant set
        blockadescope_1 = 48  # change location 2, the lower limit value of Blockade
        blockadescope_2 = 65  # change location 3, the upper limit value of Blockade
        levelmediline_1 = totalBaseline * (100 - blockadescope_1) / 100  # change location 4, the lower limit value of Amplitude
        levelmediline_2 = totalBaseline * (100 - blockadescope_2) / 100  # change location 5, the lower limit value of Amplitude
        end = 0
        baseline_be = totalBaseline
        # extract features
        print("\nRUN:")
        Y_changeFData = [(0,Y),(1,Y_xbData),(2,Y_xlowdata_1),(3,Y_xlowdata_2),(4,Y_xlowdata_3),(5,Y_xlowdata_4)]
        with Parallel(n_jobs=8) as parallel:
            output_L = parallel(delayed(te.featureFind)(clampfitData,X,Y_Blocakade,numRows,levelmediline_1,levelmediline_2,blockadescope_1,blockadescope_2,cBaselineRefer,j,totalBaseline,baseline_be,i) for i, j in Y_changeFData)
        e = 1
        output_L[0] = output_L[0].drop(['Area_0' ,'slope_0','baseline_0'],axis= 1)
        Result = output_L[0]
        for i in range(5):
            k = output_L[i + 1]
            output_L[i + 1] = output_L[i + 1].drop("Level_%d" % e,axis  =1)
            output_L[i + 1] = output_L[i + 1].drop("Area_%d" % e ,axis  =1)
            output_L[i + 1] = output_L[i + 1].drop("slope_%d" % e,axis  =1)
            output_L[i + 1] = output_L[i + 1].drop("baseline_%d" % e,axis  =1)
            output_L[i + 1] = output_L[i + 1].drop("totalBasline_%d" % e,axis  =1)
            e = e+1
            Result = pd.merge(Result, output_L[i+1], how='outer', left_index=True, right_index=True)

        Result = Result.dropna(axis=0)
        Result.to_excel(writer, sheet_name='Result')
        writer.save()
        writer.close()

        # plot the 2D-kernel density graph
        x_range_l = 50          # change location 6   x_range_l and x_range_r need in the range of blockadescope_1, blockadescope_2, and keep x_range_l< x_range_r
        x_range_r = 60          # change location 7
        y_range_l = 0           # change location 8   the lower limit value of std
        y_range_r = 5           # change location 9   the upper limit value of std
        Result_1 = np.array(Result[["Blockade_0","std_0"]])
        deleteRow = []
        for h in range(Result.shape[0]):
            if ((Result_1[h,0]>x_range_r) | (Result_1[h,0]<x_range_l) | (Result_1[h,1]<y_range_l) | (Result_1[h,1] > y_range_r) ):
                deleteRow.append(h)
        Result_2 = np.delete(Result_1,deleteRow,axis=0)
        kdePlot = sns.kdeplot(x=Result_2[:,0], y=Result_2[:,1], cmap="bwr", cbar=True, fill="fill", levels=11)
        ax = plt.gca()
        ax.set_xlim(x_range_l, x_range_r)
        ax.set_xticks(np.linspace(x_range_l, x_range_r, 5))
        xlabel = np.linspace(x_range_l, x_range_r, 5)
        xlabel = xlabel.astype(np.float32)
        ax.set_xticklabels(xlabel)
        ax.set_ylim(y_range_l, y_range_r)
        ax.set_yticks(np.linspace(y_range_l, y_range_r,5))
        ylabel = np.linspace(y_range_l, y_range_r,5)
        ylabel = ylabel.astype(np.float32)
        ax.set_yticklabels(ylabel)
        plt.savefig(path+"%s_%s.jpg" %("Blockade","std"))
        plt.show()
        plt.close()
        # Gaussian fitting
        ePbMax,ePbMin,ePsMax,ePsMin  =te.xyrange(x_range_l, x_range_r, y_range_l, y_range_r, Result_2)
        kde = gaussian_kde(Result_2.T)
        NumberOfGrid_x =100
        NumberOfGrid_y =100
        x = np.linspace(x_range_l, x_range_r,NumberOfGrid_x)
        y = np.linspace(y_range_l, y_range_r, NumberOfGrid_y)
        X, Y = np.meshgrid(x, y)
        positions = np.vstack([X.ravel(), Y.ravel()])
        # calculate the density value on the grid
        Zrank = kde(positions)
        Z = np.reshape(Zrank, X.shape)
        Z_plus = np.copy(Z)
        densityMax = np.max(Zrank)

        # let the density value which less than 1/10 of the max value of density = 0
        threshold_idx = np.where(Z_plus <= densityMax * 0.1)
        for l in range(threshold_idx[0].shape[0]):
            Z_plus[threshold_idx[0][l],threshold_idx[1][l]] =0

        minrange_X = np.floor((ePbMax-x_range_l) / (x_range_r-x_range_l)*NumberOfGrid_x).astype(int)
        min_X = np.floor((ePbMin - x_range_l) / (x_range_r - x_range_l) * NumberOfGrid_x).astype(int)
        minrange_Y = np.floor((ePsMin-y_range_l)/(y_range_r-y_range_l)*NumberOfGrid_y).astype(int)
        maxrange_Y = np.floor((ePsMax - y_range_l) / (y_range_r - y_range_l) * NumberOfGrid_y).astype(int)
        print(minrange_X,min_X,minrange_Y,maxrange_Y)

        # get the boundary of analyte and internal standard in x axis
        pereRange = np.insert(min_X,0,0)
        pereRange = np.insert(pereRange,pereRange.shape[0],NumberOfGrid_x)
        pereRange = np.sort(pereRange,axis=0)
        r = np.argwhere(Z_plus)
        leftData_x = np.unique(r[:,1])
        leftDataEdge_x = []
        for i in range(len(pereRange)-1):
            permin = pereRange[i]
            permax = pereRange[i+1]
            perleftDataIDX = np.where((leftData_x>permin) & (leftData_x < permax))
            if perleftDataIDX[0].shape[0] == 0:
                continue
            perleftData_x = leftData_x[perleftDataIDX]
            leftDataEdge_x.append(np.min(perleftData_x))
            leftDataEdge_x.append(np.max(perleftData_x))
        leftDataEdge_x = np.array(leftDataEdge_x)
        # get the boundary of analyte and internal standard in x axis
        leftDataEdge_y = []
        for j in range(0,leftDataEdge_x.shape[0],2):
            permin = leftDataEdge_x[j]
            permax = leftDataEdge_x[j+1]
            perleftDataIDy = np.where((r[:,1] > permin) & (r[:,1] < permax))
            if perleftDataIDy[0].shape[0] ==0:
                continue
            perleftData_y = r[perleftDataIDy]
            leftDataEdge_y.append(np.min(perleftData_y[:,0]))
            leftDataEdge_y.append(np.max(perleftData_y[:,0]))
        leftDataEdge_y = np.array(leftDataEdge_y)
        leftDataEdge_X = X[0,leftDataEdge_x]
        leftDataEdge_Y = Y[leftDataEdge_y,0]
        # save the analyte data and internal standard data separately
        for k in range(0,leftDataEdge_x.shape[0],2):
            perAnalyte = Result.loc[(Result["Blockade_0"]>=leftDataEdge_X[k] )& (Result["Blockade_0"]<=leftDataEdge_X[k+1])
                                    &(Result["std_0"]>=leftDataEdge_Y[k])&(Result["std_0"]<=leftDataEdge_Y[k+1])]
            sheet_name = "perAnalyte"+str(int(k/2))
            perAnalyte.to_excel(writer_2,sheet_name=sheet_name)

        leftDataEdge = np.concatenate((leftDataEdge_X,leftDataEdge_Y),axis=0)
        leftDataEdge = pd.DataFrame(leftDataEdge)
        leftDataEdge.to_excel(writer_2,sheet_name="DataEdge")
        writer_2.save()
        writer_2.close()
        print("ok")
    except Exception as err:
        print(err)
        continue





