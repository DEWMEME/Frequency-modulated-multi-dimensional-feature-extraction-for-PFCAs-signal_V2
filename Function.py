import math
import time
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.ndimage import maximum_filter, minimum_filter
from astropy.modeling import models,fitting
import warnings
import Function as te
from tqdm import tqdm


def featureFind(clampfitData,X,Y_Blocakade,numRows,levelmediline_1, levelmediline_2,blockadescope_1, blockadescope_2,cBaselineRefer,Y_xbData,totalBaseline,baseline_be,circul):
    end = 0
    clampfitNumRows = clampfitData.shape[0]
    output = np.zeros([clampfitNumRows, 13])

    for r in tqdm(range(clampfitNumRows-1), desc='Processing',leave=True,colour='white'):
        time.sleep(0.001)

        if clampfitData[r, 1] - clampfitData[r, 0] < 1.6:
            output[r, :] = 0
            continue
        start, end, bSPoint_be, bEPoint_be, bSPoint_af, bEPoint_af = te.startEnd(clampfitData[r, :], X, end, numRows,
                                                                                 cBaselineRefer)
        perData, perData_Blockade, baseline = te.perPartData(Y_xbData, start, end, bSPoint_be, bEPoint_be, bSPoint_af,
                                                             bEPoint_af,
                                                             baseline_be, r)
        if ((baseline != 0) & abs((baseline - totalBaseline) < 5)):
            baseline_be = baseline
        perData_Blockade_1 = te.perPartData_2(Y_Blocakade, start, end)
        perData_Rows = perData.shape[0]
        average_Amp = np.average(perData)
        output[r, 0] = te.discriminateLevel(average_Amp, levelmediline_1, levelmediline_2)
        output[r, 1] = np.average(perData_Blockade)
        if output[r,1] < blockadescope_1:
            output[r, :] = 0
            continue
        if output[r, 1] > blockadescope_2:
            output[r, :] = 0
            continue
        output[r, 2] = np.std(perData_Blockade)
        if (output[r, 0] == 1) | (output[r, 0] == 2):
            output[r, 3] = te.calculateArea(X, Y_xbData, start, end)
        else:
            output[r, 3] = 0

        if perData_Rows < 50:
            numbins = 7
        else:
            numbins = 10
        Fity, Std_d = te.gaussFit(perData_Blockade, output[r, 0], numbins, blockadescope_1, blockadescope_2)
        output[r, 4] = Fity
        output[r, 5] = 2 * math.sqrt(2 * math.log(2, math.e)) * Std_d  # FWHM = 2*sqrt(2*ln2)*σ

        output[r, 6] = max(perData_Blockade) - min(perData_Blockade)

        output[r, 7] = te.inclina(Y_xbData, X, start - 3)

        output[r, 8] = te.Skewness(perData_Blockade)

        output[r, 9] = te.Kurtosis(perData_Blockade)

        output[r, 10] = np.log10(clampfitData[r, 1] - clampfitData[r, 0])
        output[r, 11] = baseline
        output[r, 12] = np.average(perData_Blockade_1)
    coumns = np.array(
        ["Level_%d", "Blockade_%d", "std_%d", "Area_%d", "peak_%d", "FWHM_%d", "max-min_%d", "slope_%d", "Skewness_%d",
         "Kurtosis_%d", "log(Dwell time)_%d", "baseline_%d", "totalBasline_%d"])
    for i in range(13):
        coumns[i] = coumns[i] % circul
    output = pd.DataFrame(output, columns=coumns)
    output = output.loc[output["Level_%d" % circul] != 0]
    output = output.loc[output["Level_%d" % circul] != 2]
    return output

def startEnd(clampfitData,X,t, numRows,cBaselineRefer):
    startPoint = 0
    endPoint = 0
    numb = cBaselineRefer.shape[0]
    for e in range(t, numRows):
        if clampfitData[0] >= X[e]:
            startPoint = e
        elif clampfitData[1] > X[e]:
            endPoint = e;
        else:
            break
    baseStartPoint_be = 0
    baseEndPoint_be = 0
    k = np.argwhere(cBaselineRefer[:,2] == clampfitData[0])[0,0]
    if cBaselineRefer[k,0] == 0:
        baseEndPoint_be = startPoint-3
        for l in  reversed(range(0,startPoint)):
            if cBaselineRefer[k,1] >X[l]:
                baseStartPoint_be = l+3
                break
    else :
        for i in reversed(range(k-20,k)):
            if cBaselineRefer[i,0] == 0:
                k = i
                break
        for e in reversed(range(0,startPoint)):
            if cBaselineRefer[k,2] >= X[e]:
                baseEndPoint_be = e-3
                break
        for q in reversed(range(0,baseEndPoint_be)):
            if cBaselineRefer[k, 1] >= X[q]:
                baseStartPoint_be = q+3
                break
    baseStartPoint_af = 0
    baseEndPoint_af = 0
    k_f = np.argwhere(cBaselineRefer[:, 1] == clampfitData[1])[0, 0]
    if cBaselineRefer[k_f, 0] == 0:
        baseStartPoint_af = endPoint + 3
        for l in range(endPoint,numRows):
            if cBaselineRefer[k_f, 2] > X[l]:
                baseEndPoint_af = l - 3
                break
    else:
        if numb - k_f < 20:
            end_k_f = numb
        else:
            end_k_f = k_f + 20
        for i in range(k_f, k_f+20):
            if cBaselineRefer[i, 0] == 0:
                k_f = i
                break
        for e in range(endPoint,numRows):
            if cBaselineRefer[k_f, 1] <= X[e]:
                baseStartPoint_af = e + 3
                break
        for q in range(baseStartPoint_af,numRows):
            if cBaselineRefer[k_f, 2] <= X[q]:
                baseEndPoint_af = q - 3
                break
    if baseEndPoint_af-baseStartPoint_af<5:
        baseStartPoint_af = 0
        baseEndPoint_af = 0
    if baseEndPoint_be-baseStartPoint_be<5:
        baseStartPoint_be = 0
        baseEndPoint_be = 0
    startPoint = startPoint+3
    endPoint = endPoint-3
    return startPoint, endPoint,baseStartPoint_be,baseEndPoint_be,baseStartPoint_af,baseEndPoint_af

def perPartData(Y, start, end,bSPoint_be,bEPoint_be,bSPoint_af,bEPoint_af,baseline_be,r):
    perpartData = Y[start:end+1].reshape([end+1-start,1])
    if ((bSPoint_af == 0) & (bSPoint_be !=0)):
        baseline = np.average(Y[bSPoint_be:bEPoint_be + 1])
    elif ((bSPoint_af != 0) & (bSPoint_be ==0)):
        baseline = np.average(Y[bSPoint_af:bEPoint_af + 1])
    elif ((bSPoint_af == 0) & (bSPoint_be ==0) ):
        baseline = baseline_be
    else:
        baseline = np.average(np.concatenate((Y[bSPoint_be:bEPoint_be + 1], Y[bSPoint_af:bEPoint_af]), axis=0))
    if ((r!=1)&((baseline >baseline_be+3)|(baseline<baseline_be-3))):
        baseline = baseline_be
    perpartData_Blockade = ((baseline-perpartData)*100/baseline).reshape([end + 1 - start, 1])
    return perpartData,perpartData_Blockade,baseline

def perPartData_2(Y_Blockade, start, end):
    perpartData_Blockade = Y_Blockade[start:end+1].reshape([end+1-start,1])
    return perpartData_Blockade

def inclina (Y,X,mainPoint):
    k =abs((Y[mainPoint-1]-Y[mainPoint+1])/(X[mainPoint+1]-X[mainPoint-1]))
    return k

def discriminateLevel(average_Amp,levelmediline_1,levelmediline_2):
    if average_Amp < levelmediline_1:
        level = 0
    elif (average_Amp > levelmediline_1) & (average_Amp < levelmediline_2):
        level = 1
    else:
        level = 2
    return level

def gaussFit(perData_Blockade,level,numbins,blockadescope_1,blockadescope_2):
    perData_Blockade = pd.DataFrame(perData_Blockade, columns=["Blockade"])
    perData_Blockade_delete = perData_Blockade.drop(
        perData_Blockade[(perData_Blockade["Blockade"] < blockadescope_1) |
                         (perData_Blockade["Blockade"] > blockadescope_2)].index, axis=0)
    perData_Blockade_delete = np.array(perData_Blockade_delete)
    pershape = perData_Blockade_delete.shape[0]
    if ((level == 1) & (pershape>0) ):
        # 高斯拟合
        n, bins, patches = plt.hist(perData_Blockade_delete, numbins, density=True, facecolor='blue',alpha=0.5)  # 直方图函数，x为x轴的值，normed=1表示为概率密度，即和为一，绿色方块，色深参数0.5.返回n个概率，直方块左边线的x值，及各个方块对象
        binmiddle = (bins[1:] + bins[:-1]) / 2
        g_init = models.Gaussian1D(amplitude=np.max(n), mean=np.mean(perData_Blockade_delete), stddev=np.std(perData_Blockade_delete)) ##初始设置
        fit_g = fitting.LevMarLSQFitter() ##微调
        with warnings.catch_warnings(record=True) as w:
            g = fit_g(g_init, binmiddle, n)   ##微调
        if len(w) ==0:
            mean = g(g.mean)
            std = g.stddev
        else:
            mean = np.max(n)
            std = np.std(perData_Blockade_delete)
    else:
        mean = 0
        std = 0
    return mean,std

def gaussFit_2(data,numbins,feature,name,path):
    n, bins, patches = plt.hist(data, numbins,density=False, facecolor='blue',alpha=0.5,rwidth=0.8)  # 直方图函数，x为x轴的值，normed=1表示为概率密度，即和为一，绿色方块，色深参数0.5,返回n个概率，直方块左边线的x值，及各个方块对象
    std = np.std(data)
    mean = np.mean(data)
    binmiddle = (bins[1:] + bins[:-1]) / 2
    g_init = models.Gaussian1D(amplitude=np.mean(n), mean= mean,stddev=std,)
    fit_g = fitting.LevMarLSQFitter()
    g = fit_g(g_init,binmiddle,n)
    b_plot = np.arange(np.min(data),np.max(data),0.0001)
    plt.plot(b_plot,g(b_plot),color = "red")
    plt.ylabel(feature)

    if (feature == "Kurtosis_1")|(feature == "Skewness_0")|(feature == "Skewness_1")|(feature == "Skewness_2")|(feature == "Skewness_3")|(feature == "Skewness_4")|(feature == "Skewness_5"):
        plt.savefig(path+"%s_%s.jpg" % (name, feature))
        plt.show()
    plt.close()
    mean = g.mean
    return mean,g.stddev,g

def calculateArea(X,Y,start, end):
    perArea = 0
    for k in range(start, end):
        perAreaMin = abs((Y[k] + Y[k + 1]) * X[1] / 2)
        perArea = perArea + perAreaMin
    return perArea

def Skewness(perData):
    ave = np.average(perData)
    std = np.std(perData)
    n = len(perData)
    s = 0
    for i in range(0,n):
        ps = ((perData[i]-ave)/std)**3
        s = s +ps
    skewness= s/n
    return skewness

def Kurtosis(perData):
    ave = np.average(perData)
    std = np.std(perData)
    n = len(perData)
    s = 0
    for i in range(0,n):
        ps = ((perData[i]-ave)/std)**4
        s = s +ps
    kurtosis= s/n
    return kurtosis

def frq_sta(data1,data2,data1edge,data2edge):
    num = data1.shape[0]
    data1scal = np.linspace(data1edge[0],data1edge[1],50)
    data1slice = data1scal[1]-data1scal[0]
    data2scal = np.linspace(data2edge[0],data2edge[1],50)
    data2slice = data2scal[1]-data2scal[0]
    result = np.zeros([50,50])
    for i in range(num):
        if (data1[i]< data1edge[0]) | (data1[i]>data1edge[1]):
            continue
        if (data2[i]< data2edge[0]) | (data2[i]>data2edge[1]):
            continue
        m = int(np.floor((data1[i]-data1edge[0])/data1slice))
        n = int(np.floor((data2[i]-data2edge[0])/data2slice))
        result[m,n] = result[m,n]+1
    result= result/num
    return result

def local_extrema(data, size,mode='max'):
    if mode == 'max':
        data_filter = maximum_filter(data, size=size, mode='reflect')
        mask = data == data_filter
    elif mode == 'min':
        data_filter = minimum_filter(data, size=size, mode='reflect')
        mask = data == data_filter
    local_extrema = np.logical_and(data == data_filter, mask)
    K = np.argwhere(local_extrema)
    return K

def xyrange(x_range_l, x_range_r,y_range_l, y_range_r,Result_2):
    bins_B = np.arange(x_range_l, x_range_r + 0.04, 0.05)
    n, bins, patches = plt.hist(Result_2[:, 0], bins_B, density=False, facecolor='blue', alpha=0.5,
                                rwidth=0.8)
    print(patches.datavalues)
    plt.show()
    binmiddle = (bins_B[1:] + bins_B[:-1]) / 2
    Extreme_points_max_b = 40+local_extrema(patches.datavalues[40:bins_B.shape[0]-50],50,"max")[:,0]
    Extreme_points_min_b = Extreme_points_max_b[0]+local_extrema(patches.datavalues[Extreme_points_max_b[0]:Extreme_points_max_b[-1]],50,"min")[:,0]
    # STD
    bins_S = np.arange(y_range_l, y_range_r + 0.04, 0.05)
    n, bins, patches = plt.hist(Result_2[:, 1], bins_S, density=False, facecolor='blue', alpha=0.5,
                                rwidth=0.8)
    std = np.std(Result_2[:, 1])
    mean = np.mean(Result_2[:, 1])
    binmiddle = (bins_S[1:] + bins_S[:-1]) / 2
    g_init = models.Gaussian1D(amplitude=np.max(n), mean=mean, stddev=std)
    fit_g = fitting.LevMarLSQFitter()
    g = fit_g(g_init, binmiddle, n)
    s_plot = np.arange(np.min(y_range_l), np.max(y_range_r), 0.0001)
    fitValue = g(s_plot)
    plt.plot(s_plot, fitValue, color="red")
    plt.show()
    stdDensity_MAX = np.max(fitValue)
    stdIDX = np.argwhere(fitValue >= stdDensity_MAX*0.9)
    Extreme_points_min_s = s_plot[stdIDX[0][0]]
    Extreme_points_max_s = s_plot[stdIDX[-1][0]]

    return bins_B[Extreme_points_max_b],bins_B[Extreme_points_min_b], Extreme_points_max_s,Extreme_points_min_s