##Copyright 2023 NUID UCD. All Rights Reserved.


from dqp.core import DQPInternalModule, DQPModule, DataFrame, DataSource
import numpy as np
from .threshold import Threshold
import numpy as np
import pandas as pd
from sklearn.utils import check_array
from typing import Tuple, Union
from pycaret.anomaly import *
from .sklearn.sklof import sklof
from .sklearn.skisof import skisof
from .sklearn.skelen import skelen
from .sklearn.skonesvm import skonesvm
from pyod.models.mcd import MCD
from pyod.models.knn import KNN
from pyod.models.loda import LODA
from pyod.models.lunar import LUNAR

pycaret_models={
'Angle-base Outlier Detection': 'abod',
'Clustering-Based Local Outlier':'cluster',
'Connectivity-Based Local Outlier':'cof',
'Isolation Forest':'iforest',
'Histogram-based Outlier Detection':'histogram',
'K-Nearest Neighbors Detector':'knn',
'Local Outlier Factor':'lof',
'One-class SVM detector':'svm',
'Principal Component Analysis':'pca',
'Minimum Covariance Determinant':'mcd',
'Subspace Outlier Detection':'sod',
'Stochastic Outlier Selection':'sos',
}

sklearn_models={
'SK_one_class_svm': skonesvm, #OneClassSVM,
'SK_local_outlier_factor': sklof, #LocalOutlierFactor,
'SK_isolation_forest': skisof, #IsolationForest,
'SK_elliptic_envelope':skelen, #EllipticEnvelope,
}

pyod_models={
'pyod_mcd':MCD,
'pyod_knn':KNN,
'pyod_loda':LODA,
'pyod_lunar':LUNAR,
}

__all_models__= list(pycaret_models.values())+ list(sklearn_models.keys()) +list(pyod_models.keys()) 


_UNIVARIATE_MODELS = ["AutoRegOD"]


class AnomalyDetector(DQPInternalModule):
    _needs_fit = False
    _is_fit = False
    _needs_preprocess = False
    _is_preprocess = True

    def __init__(
        self,
        model="KNN",
        threshold_type="contamination",
        threshold_parameters={},
        lib="PyCaret",
        fraction=0.01,
        name=None,
        **params,
    ):
        self.lib=lib
        self._set_config()
        self.fraction=fraction
        self._get_threshold(threshold_type=threshold_type, **threshold_parameters)
        self._get_clf(model, **params)
        self._model_name=name


    def _set_config(self):
        if self.lib=="PyCaret":
            self._needs_preprocess = False
            self._is_preprocess = True
        else:
            self._needs_fit=True
            self._needs_preprocess=True
            self._is_preprocess = False

    def _get_clf(self, model, **params):
        if self.lib=="PyCaret":
            self._clf=None
        else:
            self._clf = model(**params)

    def _get_threshold(self, threshold_type="contamination", **params):
        self._threshold = Threshold(threshold_type=threshold_type, **params)

    def fit(self, X: np.array) -> Tuple[np.array, np.array]:
        check_array(X)
        self._clf.fit(X)
        decision_scores = self._clf.decision_scores_
        self._is_fit = True
        decision = self._threshold(decision_scores).astype(bool)
        return decision_scores, decision

    def predict(self, X: np.array) -> Tuple[np.array, np.array]:
        check_array(X)
        decision_scores, _, __ = self._clf.predict(X)
        decision = self._threshold(decision_scores)
        return decision_scores, decision

    def predict_scores(self, X: np.array) -> np.array:
        return self._clf.predict(X)


class AnomalyDetectionModule(DQPModule):
    def __init__(self, processing_options="describe", model="MultiAutoRegOD", **params):

        if model in list(pycaret_models.values()):
            self.lib="PyCaret"
        elif model in list(sklearn_models.keys()):
            self.lib="sklearn"
        else:
            self.lib="others"

        super(AnomalyDetectionModule, self).__init__(
            processing_options=processing_options, model=model, **params
        )

        self.params=params['model_config']
        if "threshold_type" in self.params:
            del self.params['threshold_type']
        if "threshold_parameters" in self.params:
            del self.params['threshold_parameters']


    @staticmethod
    def list_available_methods():
        d = {
            "tabular": [k for k in pyod_models.keys()],
            "time-series": [k for k in (list(pycaret_models.values()) + list(sklearn_models.keys()))],
        }
        return  d #__all_models__

    @staticmethod
    def get_method_params(method):
        ALL_MODELS = _PYOD_AVAILABLE_MODELS | _TODS_AVAILABLE_MODELS | sklearn_models
        assert method in ALL_MODELS, f"Unknown anomaly method: {method}"

        model = ALL_MODELS[method]
        return model.__init__.co_varnames

    def _list_available_thresholds():
        return Threshold._list_threshold_models()

    def _get_internal_module(
        self, model=None, data_type="tabular", model_config={}, **params
    ):
        self._model = model
        if data_type == "tabular":
            if model is None:
                model = "KNN"

            if  model in pyod_models:
                self._internal_module = AnomalyDetector(
                    model=pyod_models[model],lib=self.lib, name=model, **model_config
                )
            else:
                raise NotImplementedError("Unknown model. Please check if data-type is set correctly.")

        elif data_type == "time-series":
            if model is None:
                model = "iforest"

            assert model in  __all_models__
            if model in list(pycaret_models.values()):
                self._internal_module = AnomalyDetector(
                    model=model,name=model, **model_config
                )
            elif model in list(sklearn_models.keys()):
                self._internal_module = AnomalyDetector(
                    model=sklearn_models[model], name=model, lib=self.lib, **model_config
                )
            else:
                raise NotImplementedError("Unknown model. Please check if data-type is set correctly.")
        else:
            raise NotImplementedError("Unknown data-type")

        self._name = model

    def _validate_data(self, raw_data):
        if (
            len(raw_data.shape) > 1
            and raw_data.shape[1] > 1
            and self._model in _UNIVARIATE_MODELS
        ):
            raise ValueError(
                f"{self._model} only supports univariate time-series but data is of shape {raw_data.shape}"
            )

    def _preprocess(self, raw_data):
        self._validate_data(raw_data)
        return self._internal_module.fit(raw_data)

    def _process_pycaret_data(self,data):
        time_col=data._time_column
        data=data._df.copy()
        data.set_index(time_col, drop=True, inplace=True)
        data['day'] = [i.day for i in data.index]
        data['day_name'] = [i.day_name() for i in data.index]
        data['day_of_year'] = [i.dayofyear for i in data.index]
        data['week_of_year'] = [i.weekofyear for i in data.index]
        data['hour'] = [i.hour for i in data.index]
        data['is_weekday'] = [i.isoweekday() for i in data.index]
        if data.index.duplicated().sum()>0:
            data.reset_index(inplace=True,drop=True)
        return data

    def _process(self,raw_data):
        if self.lib=="PyCaret":
            return self._process_pycaret(raw_data)
        else:
            return self._process_others(raw_data)


    def _process_others(self,raw_data):

        self._validate_data(raw_data)
        scores, decision = self._internal_module.predict(raw_data)
        return scores, decision

    def _process_pycaret(self, raw_data):
        self._validate_data(raw_data._df)
        raw_data=self._process_pycaret_data(raw_data)
        s = setup(raw_data, session_id = 123,verbose=False)

        # train model
        if  self._internal_module._threshold._name=="contamination":
                self._internal_module._clf = create_model(self._internal_module._model_name, fraction =self._internal_module._threshold.thresh.contamination,**self.params)
        else:
                self._internal_module._clf = create_model(self._internal_module._model_name, fraction =0.05,**self.params)

        results = assign_model(self._internal_module._clf)
        #print(results)
        scores=results['Anomaly_Score'].values
        if  self._internal_module._threshold._name=="contamination":
            decision=results['Anomaly'].astype(bool).values #self._internal_module.predict(raw_data)
        else:
            decision=self._get_decision_pythresh(scores)
        return scores, decision

    def _get_decision_pythresh(self, scores):

        decision=self._internal_module._threshold.eval(scores)
        return decision.astype(bool)

    def _describe(self, result, data: Union[DataFrame, DataSource], raw_data, **kwargs):
        (scores, decision) = result

        if isinstance(data, DataFrame):
            df = data
        else:
            df = data._df

        df["_is_anomaly"] = decision
        df["_anomaly_score"] = scores
        data._annotation_columns.extend(["_is_anomaly", "_anomaly_score"])
        return data

    def _remove(self, result, data: Union[DataFrame, DataSource], raw_data, **kwargs):
        (scores, decision) = result

        if isinstance(data, DataSource):
            data._df = data._df[~decision]
        else:
            data = data[~decision]
        return data


__all__ = ["AnomalyDetectionModule"]
