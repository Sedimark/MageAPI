## Copyright 2023 NUID UCD. All Rights Reserved.

from ..core import DQPInternalModule, DQPModule, DataFrame, DataSource
import numpy as np
from ..dtypes import _NUMERIC_DTYPES
import warnings
from typing import Union
import pandas as pd
from .imputers import _AVAILABLE_IMPUTERS
    

class MissingImputation(DQPInternalModule):
    
    """
    
    How to handle both categorical and numeric dtypes?
    
    """
    
    _needs_fit=True
    _is_fit =False
    _needs_preprocess=True
    _is_preprocess=False
    
    def __init__(self, imputation_method='average', **params):
        
        self._get_imputer(imputation_method, **params)
        
    
    
    def _get_imputer(self, imputation_method='SimpleImputer', imputer_strategy='most_frequent',**params):
        
        assert imputation_method in _AVAILABLE_IMPUTERS
        self._imputer = _AVAILABLE_IMPUTERS[imputation_method](**params)
        self._imputation_method = imputation_method
        
    def fit(self, raw_data):
      
        self._imputer.fit(raw_data)
        self._is_fit=True
        print('predicting')
        return self.predict(raw_data)
    
    
    def predict(self, raw_data):
        
        if hasattr(self._imputer, 'transform'):
            return self._imputer.transform(raw_data)
        elif hasattr(self._imputer, 'solve'):
            return self._imputer.solve(raw_data)
        
        else:
            raise ValueError('No transformation method???')

class MissingImputationModule(DQPModule):
    
   
    def __init__(self, processing_options=['transform'], **params):
        
        super(MissingImputationModule, self).__init__(self, processing_options=processing_options, **params)
    
    @staticmethod
    def list_available_methods():
        
        
        return [k for k,v in _AVAILABLE_IMPUTERS.items()]
    
    @staticmethod
    def get_method_params(method):
        
        assert method in _AVAILABLE_IMPUTERS, f'Unknown imputation method: {method}'
        
        model = _AVAILABLE_IMPUTERS[method]
        return model.__init__.co_varnames
        
         
    def _get_internal_module(self, imputation_method='Interpolation',model_config={},**params):
        self._internal_module = MissingImputation(imputation_method=imputation_method, **model_config)
        self._imputation_method = imputation_method
        
    def _transform(self, result:np.array,data:Union[DataFrame,DataSource], raw_data:np.array, mapping=None) -> DataFrame:
        
        #TODO Here we might actually need to know the mapping etc, e.g if we have converted columns.

        if isinstance(data, DataSource):
            df=data._df
        else:
            df=data
        
        if mapping:
        
        

            for idx, col in enumerate(mapping):
                
                df[col] = result[:,idx]
                
        else:
            
            for col in result.columns:
                
                df[col] = result[col]
        
        return data
    
    def _prepare_data(self, data:Union[DataFrame, DataSource]):
        
        ignore_columns = [data._time_column]
        valid_columns = [col for col in data.columns if col not in ignore_columns]
        
        if isinstance(data, DataSource):
            df=data._df.copy()
        else:
            df=data.copy()
        
        if self._imputation_method in ['SimpleImputer']:
      
            return df, None
        
        elif self._imputation_method in ['KNNImputer', 'Interpolation','NuclearNormMinimization',
        'MatrixFactorization','IterativeSVD', 'SoftImpute', 'BiScaler','SimilarityWeightedAveraging']:
            
            if data._numeric_columns:
                numeric_columns = data._numeric_columns
            else:
                numeric_columns = [col for col in data.columns if df[col].dtype in _NUMERIC_DTYPES]

            return df[numeric_columns].values.astype(np.float64), numeric_columns
        
        elif self._imputation_method in ['LogisticRegression']:
            
            return data, None
        else:
            raise NotImplementedError(f'Unknown method {self._imputation_method}')

    
    def _preprocess(self, raw_data):
        
        
        return self._internal_module.fit(raw_data)
        
    def _process(self, raw_data):
        
        raw_data = self._internal_module.predict(raw_data)

        return raw_data
        
        
