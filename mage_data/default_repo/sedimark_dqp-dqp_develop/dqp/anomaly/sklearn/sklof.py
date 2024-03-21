##Copyright 2023 NUID UCD. All Rights Reserved.


from sklearn.neighbors import LocalOutlierFactor




class sklof(LocalOutlierFactor):


    def __init__(self,**params):
         super().__init__(**params)




    def fit(self,X,y=None):
        
        super().fit(X,y)
        self.decision_scores_=-self.negative_outlier_factor_

        return self
