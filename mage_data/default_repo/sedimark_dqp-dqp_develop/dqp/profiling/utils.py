##Copyright 2023 NUID UCD. All Rights Reserved.


import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MinMaxScaler
from scipy.stats import pearsonr


def normalised_entropy(data):
    ####  from Lorena, Ana C., et al. "Analysis of complexity indices for classification problems: Cancer gene expression data." Neurocomputing 75.1 (2012): 33-42.
    counts = data.value_counts() 
    probs = counts / counts.sum()
    return -(1 / np.log(len(counts))) * (probs * np.log(probs)).sum()


def imbalance_ratio(data):
    counts = data.value_counts()
    return np.max(counts) / np.min(counts)



def lrid(data):
    #### based on Zhu, Rui, et al. "LRID: A new metric of multi-class imbalance degree based on likelihood-ratio test." Pattern Recognition Letters 116 (2018): 36-42.
    C=len(data.unique())
    freq=data.value_counts()
    sum=0
    for i in range(C):
        sum+=(freq[i])* np.log(len(data)/(C*freq[i]))
    return -2*sum



class Imbalance:
    def __init__(self, metrics=["IR"]):
        methods = {
            "IR": imbalance_ratio,
            "LLI": lrid,
            "NE": normalised_entropy,
        }

        if isinstance(metrics, str):
            if metrics == "all":
                metrics = [method for method in methods]
            else:
                metrics = [metrics]

        self._methods = {metric: methods[metric] for metric in methods}

    def __call__(self, data):
        return {metric: self._methods[metric](data) for metric in self._methods}



def F1(X, y):
    """
    Calculates F1 score, Fisher's discriminant ratio as defined in
    Lorena, Ana C., et al. "How complex is your classification problem? a survey on measuring classification complexity." ACM Computing Surveys (CSUR) 52.5 (2019): 1-34.
    and in
    Orriols-Puig, Albert, Núria Macia, and Tin Kam Ho. "Documentation for the data complexity library in c++." Universitat Ramon Llull, La Salle 196.1-40 (2010): 12.
    """
    f1_list = []
    classes=pd.unique(y)
    nominator=0
    denominator=0
    for m in range(len(classes)):
        i=classes[m]
        c1=X[y==i]
        for n in range(m+1,len(classes)):
            j=classes[n]
            if i!=j:
                c2=X[y==j]
                nominator+=(len(c1)/len(X))*(len(c2)/len(X))*((c1.mean()-c2.mean()))**2
        denominator+=(len(c1)/len(X))*c1.std()**2
    f1_list.append(nominator/denominator)
    return (1/(1+np.max(f1_list)))



def is_categorical(
    col, method="fraction_unique", cat_cols=None, min_fraction_unique=0.05
):
    """Removes categorical features using a given method.
    X: pd.DataFrame, dataframe to remove categorical features from."""

    if method == "fraction_unique":
        return (len(pd.unique(col)) / len(col)) < min_fraction_unique

    if method == "named_columns":
        return col.name not in cat_cols

    return False


class SimpleColinearityChecker:

    """
    Predict each variable using N-1 variables, and report correlation.
    """

    name = "simple-colinearity-checker"

    def __init__(self, model=LinearRegression):
        self._model = model

    def __call__(self, df, datecols=None, target_columns=None):
        Scaler = lambda x: MinMaxScaler().fit_transform(x)
        df = df.copy()
        if not target_columns:
            target_columns = [
                col
                for col in df.columns
                if (
                    (datecols == None or col not in datecols)
                    and df[col].isnull().any() != True
                    and len(df[col].unique()) > 1
                    and len(df[col].astype("category").cat.codes.unique())
                )
            ]
        if len(target_columns)<2:
            return None, None, None, None
        newcols = []
        for col in target_columns:
            if df[col].dtype == "object":
                df[col + "_cat"] = df[col].astype("category").cat.codes
                target_columns[target_columns.index(col)] = col + "_cat"
                newcols.append(col + "_cat")

        output1 = {}
        output2 = {}
        output3 = {}
        for idx in range(len(target_columns)):
            target = df[target_columns[idx]].values
            target = Scaler(target.reshape(-1, 1))
            feature = df[
                [target_columns[j] for j in range(len(target_columns)) if j != idx]
            ].values
            model = self._model()

            model.fit(feature, target)
            pred = model.predict(feature)

            cor = pearsonr(pred.flatten(), target.flatten())
            output1[target_columns[idx]] = cor
            output2[target_columns[idx]] = pred
            output3[target_columns[idx]] = target
        #        df=df.drop(newcols,axis=1)
        return np.mean([output1[k][0] for k in output1]), output1 # , output2, output3

    def format_result(self, result):
        mean, output1, output2, output3 = result
        string = f"A mean colinearity of {np.round(mean,2)} was found between the columns in the data\n"
        return string


def unalikeability(column):
    freq = column.value_counts()

    result = 0
    if len(np.unique(column)) != len(column):
        for val in freq.values:
            result += (val / len(column)) ** 2
    return 1 - result
