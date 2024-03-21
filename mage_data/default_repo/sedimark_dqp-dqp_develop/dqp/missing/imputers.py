## Copyright 2023 NUID UCD. All Rights Reserved.

from ..core import DQPInternalModule, DQPModule, DataFrame, DataSource
import numpy as np
from sklearn.impute import SimpleImputer as SimpleImputerSK, KNNImputer as KNNImputerSK
from ..dtypes import _NUMERIC_DTYPES
import warnings
from typing import Union
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.utils import check_array
from sklearn.preprocessing import LabelEncoder


def filter_params(model, params):
    vars = model.__init__.__code__.co_varnames

    params = {param: params[param] for param in params if param in vars}
    return params


class SimpleImputer(SimpleImputerSK):
    _needs_fit = True
    _is_fit = False

    def __init__(
        self,
        missing_values=np.nan,
        strategy="most_frequent",
        target_columns=[],
        **kwargs,
    ):
        self._imputer = SimpleImputerSK(
            missing_values=missing_values, strategy=strategy
        )
        self._target_columns = target_columns

    def fit(self, df):
        if not self._target_columns:
            self._target_columns = df.columns
        X = df[self._target_columns].values
        #### fix output column datatypes
        coltypes=df.dtypes
        self._imputer.fit(X)
        self._is_fit = True
        df[self._target_columns] = self._imputer.transform(X)
        for col in self._target_columns:
            df[col]=df[col].astype(coltypes[col])
        return df

    def transform(self, df):
        coltypes=df.dtypes
        X = self._imputer.transform(df[self._target_columns].values)
        df[self._target_columns] = X
        for col in self._target_columns:
            df[col]=df[col].astype(coltypes[col])
        return df


class KNNImputer(KNNImputerSK):
    def __init__(
        self,
        missing_values=np.nan,
        n_neighbors=5,
        weights="uniform",
        metric="nan_euclidean",
        **kwargs,
    ):
        super(KNNImputer, self).__init__(
            missing_values=missing_values,
            n_neighbors=n_neighbors,
            weights=weights,
            metric=metric,
        )


class InterpolationImputer:
    def __init__(self, window_size=5, **params):
        self._window_size = window_size

    def fit(self, data: np.array):
        pass

    def transform(self, data: np.array):
        data = data.copy()
        for col in range(data.shape[1]):
            nans = np.isnan(data[:, col])
            if nans.any():
                data[:, col] = self._impute_col(data[:, col])
        return data

    def _impute_col(self, vals):
        vals = pd.Series(vals).interpolate(method="linear").values
        # Interpolate may leave nans at start of series, if series starts in nan
        # Just fill these with first non-nan value
        still_nan = np.isnan(vals)
        if still_nan.any():
            c = np.argwhere(still_nan == 0)[0][0]
            vals[:c] = vals[c]

        return vals


class LogisticRegressionImputer:
    def __init__(
        self,
        Y_columns=[],
        X_columns=[],
        model=LogisticRegression,
        **params,
    ):
        self.X_columns = X_columns
        self.Y_columns = Y_columns

    def fit(self, data: Union[DataSource, DataFrame]) -> None:
        if not self.X_columns:
            self.X_columns = data._numeric_columns

        if not self.Y_columns:
            self.Y_columns = data._categorical_columns

        assert len(self.X_columns) > 0 and len(self.Y_columns) > 0

        if isinstance(data, DataSource):
            df = data._df.copy()
        else:
            df = data.copy()

        for col in self.X_columns:
            print("name",col)
            assert not np.isnan(
                df[col].values
            ).any(), f"Input column {col} contains np.nan"

        self._clfs = {}
        self._encoders = {}
        X = df[self.X_columns].values.astype(np.float32)

        for col in self.Y_columns:
            Y = df[col]

            print(col)
            non_null = ~Y.isnull()

            encoder = LabelEncoder().fit(Y[non_null].values)
            Y_values = encoder.transform(Y[non_null].values)
            model = LogisticRegression()
            model.fit(X[non_null], Y_values)
            self._clfs[col] = model
            self._encoders[col] = encoder

    def transform(
        self, data: Union[DataFrame, pd.DataFrame]
    ) -> Union[DataFrame, pd.DataFrame]:
        if isinstance(data, DataSource):
            df = data._df.copy()
        else:
            df = data.copy()

        for col in self.Y_columns:
            null = df[col].isnull()
            if not null.any():
                continue
            X = df[self.X_columns][null]
            Y_pred = self._clfs[col].predict(X)
            df[col][null] = self._encoders[col].inverse_transform(Y_pred)

        return df


_AVAILABLE_IMPUTERS = {
    "SimpleImputer": SimpleImputer,
    "KNNImputer": KNNImputer,
    "LogisticRegression": LogisticRegressionImputer,
    "Interpolation": InterpolationImputer,
}


try:
    from fancyimpute import (
        NuclearNormMinimization,
        MatrixFactorization,
        IterativeSVD,
        SimpleFill,
        SoftImpute,
        BiScaler,
        KNN,
        SimilarityWeightedAveraging,
        IterativeImputer,
    )

    algorithms = (
        NuclearNormMinimization,
        MatrixFactorization,
        IterativeSVD,
        SoftImpute,
        BiScaler,
        KNN,
        SimilarityWeightedAveraging,
    )

    for algo in algorithms:
        continue

        name = str(algo).split(".")[2].split("'")[0]

        class Wrapper:
            def __init__(self, model):
                self._model = model

            def __repr__(self):
                return str(self._model)

            def __call__(self, **params):
                params = filter_params(self._model, params)
                return self._model(**params)

        _AVAILABLE_IMPUTERS[name] = Wrapper(algo)


except:
    warnings.warn("Fancy impute not installed, some methods are unavailable")


try:
    from autoimpute.imputations import SingleImputer, MultipleImputer, MiceImputer

    class AutoImputeSingle(SingleImputer):
        def __init__(self, **params):
            super(AutoImputeSingle, self).__init__(
                **filter_params(SingleImputer, params)
            )

    class AutoImputeMultiple(MultipleImputer):
        def __init__(self, **params):
            super(AutoImputeSingle, self).__init__(
                return_list=True, **filter_params(MultipleImputer, params)
            )

    class AutoImputeMice(MiceImputer):
        def __init__(self, **params):
            super(AutoImputeSingle, self).__init__(
                return_list=True, **filter_params(MiceImputer, params)
            )

    # _AVAILABLE_IMPUTERS |= {
    #     "AutoImputeSingle": AutoImputeSingle,
    #     "AutoImputeMultiple": AutoImputeMultiple,
    #     "AutoImputeMice": AutoImputeMice,
    # }

except:
    warnings.warn(
        "Could not locate autoimpute package, some imputation methods will be unavailable."
    )
