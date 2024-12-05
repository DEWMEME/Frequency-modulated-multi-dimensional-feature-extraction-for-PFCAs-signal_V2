clear;
clc;
set(0,'DefaultFigureWindowStyle','docked'); 
% The function selectData ,selectData_2 should do some slight change for
% different porpose

%% This part can obtain the sequence of feature ,according to the contribution to improving the identification accuracy
This is suitable to 43 features. For 8 features, need do some slight
change
Sequence_va = cell(43,1);
Sequence_acc = []; 
feature = linspace(2,43,42);
pathFile = '/home/zx/LHS/test\';  % change location to your own laptop 
ClassLabel = ['C0','C2','3H',"C3","3Cl",'C4','5H','C5','33FTCA','C6','7H','C7','C8','C9'];
for i = 1:43
    if i == 1
        [Train,Predict] = selectData(200,40,[]);
        features = Train.Properties.VariableNames;
        [numr,numc] = size(Train);
        t = templateTree("MinParentSize",2,"MaxNumSplits",numr-1,"MinLeafSize",1,"NumVariablesToSample",7,"MergeLeaves","off","Prune","off");
        baggModel =fitcensemble(Train(:,1),Train(:,44),"Method","Bag","Learners",t,'NumLearningCycles',30);
        CdtModel = crossval(baggModel);
        cvLabel = char(kfoldPredict(CdtModel)); 
        classLoss = kfoldLoss(CdtModel);
        pLabel= char(predict(baggModel,Predict(:,1)));
        predictfact =char(table2cell(Predict(:,44)));
        trainfact =char(table2cell(Train(:,44)));
        [numc,numl] = size(predictfact);
        ACCture = 0;
        for j = 1:numc
            if predictfact(j) == pLabel(j)
                ACCture = ACCture+1;
            end
        end
        path = [pathFile,'RUN1_Blocakde','.jpg'];
        gcf = figure("Name",'Blocakde');
        cm = confusionchart(trainfact,cvLabel);
        sortClasses(cm,ClassLabel); 
        cmValues = cm.NormalizedValues; 
        cmValues_total = cmValues;
        k = strcat("Blockade_\",num2str((1-classLoss)*100));
        cm.Title = k;
        saveas(gcf,path); 
        predictACC = ACCture/numc;
        Sequence_va{i} = "Blockade";
        Sequence_acc(1,1) = (1-classLoss)*100;
        Sequence_acc(1,2) = predictACC*100;
        sequence_select = [1];
    else
        fprintf("The %d times\n",i);
        [numfc,numfl] = size(feature);
        perRoundAcc = [];
        perRoundPredict = [];
        for m = 1: numfl
            fprintf("The %d times _%d\n",i,m);
            featureselect = [sequence_select,feature(m)];
            baggModel =fitcensemble(Train(:,featureselect),Train(:,44),"Method","Bag","Learners",t,'NumLearningCycles',30);
            CdtModel = crossval(baggModel);
            cvLabel = char(kfoldPredict(CdtModel)); 
            classLoss = kfoldLoss(CdtModel);
            useData = Predict(:,featureselect); 
            o = predict(baggModel,useData);
            pLabel= char(predict(baggModel,Predict(:,featureselect)));
            predictfact =char(table2cell(Predict(:,44)));
            trainfact =char(table2cell(Train(:,44)));
            [numc,numl] = size(predictfact);
            ACCture = 0;
            for j = 1:numc
                if predictfact(j) == pLabel(j)
                    ACCture = ACCture+1;
                end
            end
            predictACC = ACCture/numc;
            perRoundAcc = [perRoundAcc,(1-classLoss)*100];
            perRoundPredict= [perRoundPredict,predictACC*100];
            name = char(features(feature(m)));
            path = [pathFile,'RUN1_',name,'.jpg'];
            gcf = figure("Name",name);
            cm = confusionchart(trainfact,cvLabel);
            sortClasses(cm,ClassLabel); 
            cmValues = cm.NormalizedValues; 
            cmValues_total = [cmValues_total;cmValues];
            k =strcat(cellstr(features(feature(m))),'_\',num2str(i),'_\',num2str((1-classLoss)*100));
            cm.Title = k;
            saveas(gcf,path);  
        end
        [n,p] = max(perRoundAcc);
        sequence_select = [sequence_select,feature(p)];
        Sequence_va{i} = features(feature(p));
        Sequence_acc(i,1) = perRoundAcc(p);
        Sequence_acc(i,2) = perRoundPredict(p);
        feature(p) = [];
        if i == 42
            Sequence_va{i+1} = features(feature(1));
           baggModel =fitcensemble(Train(:,1:43),Train(:,44),"Method","Bag","Learners",t,'NumLearningCycles',30);
            CdtModel = crossval(baggModel);
            classLoss = kfoldLoss(CdtModel);
            pLabel= char(predict(baggModel,Predict(:,1:43)));
            predictfact =char(table2cell(Predict(:,44)));
            [numc,numl] = size(predictfact);
            ACCture = 0;
            for j = 1:numc
                if predictfact(j) == pLabel(j)
                    ACCture = ACCture+1;
                end
            end
            path = [pathFile,features(feature(1)),'.jpg'];
            gcf = figure("Name",features(feature(1)));
            cm = confusionchart(trainfact,cvLabel);
            cmValues_total = [cmValues_total;cmValues];
            cmValues = cm.NormalizedValues .* cm.NormalizationDenominator;
            savefig(gcf,path);
            predictACC = ACCture/numc;
            Sequence_acc(43,1) = (1-classLoss)*100;
            Sequence_acc(43,2) = predictACC*100;
            break
        end
    end
end
% the result save location, you should change to your own laptop 
writematrix( Sequence_acc,"/home/zx/LHS/test/result_Bagging.xlsx","Sheet","result");

%% This part is for 3 analytes(FTA,C5,C6) in specific dataset size
% this is suitable for datasize = 50, if change the size, some slight
% change need to do
fprintf("50\n");
Sequence_acc_50 = []; 
Sequence_va_50 = cell(43,5);
feature = linspace(2,43,42);
for k = 1:5   % repeat 5 times
    feature = linspace(2,43,42);
    [Train,features] = selectData_2(50,50,50,[]);
    [numr,numc] = size(Train);
    analyte = unique(Train(:,44));
    for i = 1:43
        if i == 1
            t = templateTree("MinParentSize",2,"MaxNumSplits",numr-1,"MinLeafSize",1,"NumVariablesToSample",7,"MergeLeaves","off","Prune","off");
            baggModel =fitcensemble(Train(:,1),Train(:,44),"Method","Bag","Learners",t,'NumLearningCycles',30);
            CdtModel = crossval(baggModel);
            cvLabel = char(kfoldPredict(CdtModel));
            classLoss = kfoldLoss(CdtModel);
            Sequence_acc_50(1,k) = (1-classLoss)*100;
            sequence_select = [1];
            Sequence_va_50{1,k} = 'Blockade';
        else
            fprintf("第%d轮\n",i);
            [numfc,numfl] = size(feature);
            perRoundAcc = [];
            perRoundPredict = [];
            for m = 1:numfl
                fprintf("第%d轮_%d\n",i,m);
                featureselect = [sequence_select,feature(m)];
                baggModel =fitcensemble(Train(:,featureselect),Train(:,44),"Method","Bag","Learners",t,'NumLearningCycles',30);
                CdtModel = crossval(baggModel);
                cvLabel = char(kfoldPredict(CdtModel)); 
                classLoss = kfoldLoss(CdtModel);
                perRoundAcc = [perRoundAcc,(1-classLoss)*100];
            end
            [n,p] = max(perRoundAcc);
            sequence_select = [sequence_select,feature(p)];
            Sequence_va_50{i,k} = features(feature(p));
            Sequence_acc_50(i,k) = perRoundAcc(p);
            feature(p) = [];
            if i == 42
                Sequence_va_50{i+1,k} = features(feature(1));
                baggModel =fitcensemble(Train(:,1:43),Train(:,44),"Method","Bag","Learners",t,'NumLearningCycles',30);
                CdtModel = crossval(baggModel);
                classLoss = kfoldLoss(CdtModel);
                Sequence_acc_50(43,k) = (1-classLoss)*100;
                break
            end
        end
    end
end

%% This part is for different datasize for FTA,C5,C6
Sequence_va = cell(43,1);
Sequence_acc = []; 
selectFeatures = [1,5,8,3,6,7,4,2,11,12,14,9,10,15,13,18,19,17,22,36,20,25,21,24,44];
datause = 9000;
ftca = [datause,datause/2,datause/5,datause/10,datause/20,datause/50,datause/100,datause/200,datause/500,datause/1000];
ClassLabel = ["C5","33FTCA","C6"];
for h  = 1:10
    fprintf("run%d\n" ,h);
    t = templateTree("MinParentSize",2,"MaxNumSplits",ftca(h)+2*datause-1,"MinLeafSize",1,"NumVariablesToSample",7,"MergeLeaves","off","Prune","off");
    for i = 1:10
        [Train] = selectData_2(ftca(h),datause,datause,selectFeatures);
        trainfact =table2cell(Train(:,end));
        fprintf("Training RUN%d.....\n", i );
        baggModel =fitcensemble(Train(:,1:end-1),Train(:,end),"Method","Bag","Learners",t,'NumLearningCycles',30);
        CdtModel = crossval(baggModel);
        classLoss = kfoldLoss(CdtModel);
        cvLabel = kfoldPredict(CdtModel);
        cm = confusionchart(trainfact,cvLabel);
        sortClasses(cm,ClassLabel);
        cmValues = cm.NormalizedValues; 
        Sequence_acc((h-1)*10+i,1) =  ftca(h);
        Sequence_acc((h-1)*10+i,2) =  datause;
        Sequence_acc((h-1)*10+i,3) =  datause;
        Sequence_acc((h-1)*10+i,4) =  sum(cmValues(:,1));
        Sequence_acc((h-1)*10+i,5) =  sum(cmValues(:,2));
        Sequence_acc((h-1)*10+i,6) =  sum(cmValues(:,3));
    end
end