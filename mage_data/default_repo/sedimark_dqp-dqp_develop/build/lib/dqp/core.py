##Copyright 2023 NUID UCD. All Rights Reserved.

import pandas as pd
import numpy as np
import datetime
import pickle
import os
import sys
from .dtypes import _NUMERIC_DTYPES, _CATEGORICAL_DTYPES
import copy
from typing import Union
from collections import namedtuple
import pickle


class DataFrame(pd.DataFrame):

    """
    Basic SEDIMARK internal data format.
    Either one, or a collection of dataframes?

    """

    # TODO Overloading pd.DataFrame is probably not going to work
    # in the longrun

    _name = "SedimarkDataFrame"
    _meta_data = {}
    _time_column = None
    _numeric_columns = []
    _ignore_columns = []
    _categorical_columns = []
    _index_column = []
    _is_time_series = False
    _valid_ranges = {}
    # features to model
    _target_features = None
    _test_columns = []
    _df_profile = (None,)
    _column_profiles = ([],)
    _description = (None,)
    _column_profiles = None
    _id_column = None
    _test_columns = []
    _annotation_columns = []

    def __init__(
        self,
        df,
        test_columns=None,
        time_column=None,
        numeric_columns=[],
        categorical_columns=[],
        valid_ranges={},
        **params,
    ):
        if isinstance(df, dict):
            df = pd.DataFrame(df)

        for attr in df.__dict__:
            setattr(self, attr, df.__dict__[attr])

        if test_columns is not None:
            self._test_columns = test_columns

        self._time_column = time_column
        self._numeric_columns = numeric_columns
        self._categorical_columns = categorical_columns
        self._valid_ranges = valid_ranges

    def dataframe_to_numpy_array(self, df):
        """

        Generic function for getting np.float32 array from pd.DataFrame

        """

        # bad
        return self.values

    @staticmethod
    def concat(data_frames, axis=0):
        attrib_df = None
        for df in data_frames:
            if isinstance(df, DataFrame):
                attrib_df = df
        df = pd.concat(data_frames, axis=axis)
        df = DataFrame(df)
        if attrib_df is not None:
            for attr in [
                "_categorical_columns",
                "_numeric_columns",
                "_test_columns",
                "_ignore_columns",
                "_meta_data",
                "_valid_ranges",
                "_df_profile",
                "_column_profiles",
                "_id_column",
                "_time_column",
                "_annotation_columns",
            ]:
                setattr(df, attr, copy.deepcopy(getattr(attrib_df, attr)))

        return df

    def drop(self, *args, **kwargs):
        result = super().drop(*args, **kwargs)
        df = DataFrame(result)
        return self._copy_local_attributes(df)

    def __getitem__(self, key):
        result = super().__getitem__(key)

        # if indexing produces a new dataframe
        if isinstance(result, pd.DataFrame):
            df = DataFrame(result)
            return self._copy_local_attributes(df)
        # Otherwise if this is a column
        elif isinstance(result, pd.Series):
            return result

    def sort_values(self, **kwargs):
        df = super().sort_values(**kwargs)
        df = DataFrame(df)
        df = self._copy_local_attributes(df)
        return df

    def _copy_local_attributes(self, df):
        # TODO if the new df has less columns,
        # they are still going to get copied across here  :(

        for attr in [
            "_categorical_columns",
            "_numeric_columns",
            "_test_columns",
            "_ignore_columns",
            "_meta_data",
            "_valid_ranges",
            "_df_profile",
            "_column_profiles",
            "_id_column",
        ]:
            setattr(df, attr, copy.deepcopy(getattr(self, attr)))
        df._valid_ranges = self._valid_ranges

        return df


class DataSource:
    _name = "SedimarkDataFrame"
    _meta_data = {}
    _time_column = None
    _numeric_columns = []
    _ignore_columns = []
    _categorical_columns = []
    _index_column = []
    _is_time_series = False
    _valid_ranges = {}
    # features to model
    _target_features = None
    _test_columns = []
    _df_profile = (None,)
    _description = (None,)
    _column_profiles = None
    _test_columns = []
    _annotation_columns = []

    def __init__(
        self,
        df: pd.DataFrame,
        test_columns=[],
        time_column=None,
        numeric_columns=[],
        categorical_columns=[],
        valid_ranges={},
        **params,
    ):
        self._df = df
        self._time_column = time_column
        self._numeric_columns = numeric_columns
        self._categorical_columns = categorical_columns
        self._valid_ranges = valid_ranges
        self._test_columns = test_columns

    @property
    def columns(self):
        return self._df.columns

    def __repr__(self):
        return self._df.__repr__()


class DQPInternalModule:
    _needs_fit = False
    _is_fit = True
    _needs_preprocess=False
    _is_preprocess=False

    @property
    def requires_fit(self):
        return self._needs_fit and (not self._is_fit)

    @property   
    def requires_preprocess(self):
        return self._needs_preprocess and (not self._is_preprocess)

class DQPModule:

    """

    Process data using an underlying DQ tool.
    The DQP module handles any manipulation of the data object.
    The base module does the specific processing of the transformed data.

    """

    def __init__(
        self,
        verbose=True,
        processing_options=[],
        categorical_encoding_limit=10,
        data_type="tabular",
        **params,
    ):

        self._set_module_params(
            verbose=verbose,
            categorical_encoding_limit=categorical_encoding_limit,
            data_type=data_type,
            **params,
        )

        self._get_internal_module(data_type=data_type, **params)
        self._get_processing_ops(processing_options=processing_options, **params)

    def __call__(self, df: DataFrame, **params) -> DataFrame:
        return self.process(df, **params)

    def _get_available_opts(self) -> None:
        """
        Check which processing options the inheriting class implements
        """

        _available_opts = {}

        for opt in ["describe", "annotate", "transform", "remove", "augment"]:
            if hasattr(self, f"_{opt}"):
                _available_opts[opt] = getattr(self, f"_{opt}")
        return _available_opts

    def _get_internal_module(self, **params) -> None:
        raise NotImplementedError

    def _set_module_params(
        self,
        categorical_encoding_limit=10,
        data_type="tabular",
        verbose=False,
        **params,
    ) -> None:
        self._categorical_encoding_limit = categorical_encoding_limit
        self._data_type = data_type
        self.verbose = verbose

    def _get_processing_ops(self, processing_options: list = [], **params) -> None:
        """

        Check which of the supplied processing options are valid,and add them to pipeline.

        """

        # TODO Should this just be limited to one transformation of the data?
        self._available_opts = self._get_available_opts()
        self._internal_pipeline = []

        if isinstance(processing_options, str):
            processing_options = [processing_options]

        for opt in processing_options:
            assert (
                opt in self._available_opts
            ), f"{opt} is not an available processing option for {str(self)}"

            self._internal_pipeline.append(self._available_opts[opt])

    def process(
        self,
        data: Union[DataFrame, np.array, dict, DataSource],
        output_path=None,
        **params,
    ) -> DataFrame:


        if self._internal_module.requires_preprocess:
            raw_data, mapping = self._prepare_data(data)
            self._validate_data(raw_data)
        else:
            raw_data=data
            mapping=None

        if self._internal_module.requires_fit:
            result = self._preprocess(raw_data, **params)
        else:
            result = self._process(raw_data, **params)

        data = self._handle_result(result, data, raw_data, mapping=mapping)

        if output_path:
            self._save_output(data, output_path)

        return data

    def _save_output(data: Union[DataFrame, DataSource], output_path: str):
        with open(output_path, "wb") as handle:
            handle.write(data)

    @staticmethod
    def load_saved_output(path: str):
        with open(path, "rb") as handle:
            return pickle.load(handle)

    def preprocess(self, data: Union[DataFrame, np.array, dict], **params) -> DataFrame:
        """
        Fit internal  modules to data without transforming it
        """

        raw_data, mapping = self._prepare_data(data)

        self._validate_data(raw_data)

        result = self._preprocess(raw_data, **params)

        return result

    def _prepare_data(self, df: DataFrame):
        return self._get_numpy(df)

    def _handle_result(self, result, df, raw_data, **kwargs):
        for opt in self._internal_pipeline:
            df = opt(result, df, raw_data, **kwargs)

        return df

    def _preprocess(self, df: DataFrame, **params):
        pass

    def _process(self, df: DataFrame, **params):
        pass

    def _validate_data(self, data: np.array):
        pass

    def _get_numpy(self, data: Union[DataFrame, DataSource]) -> np.array:
        """

        Convert dataframe to numpy representation.

        """

        # TODO This method likely needs params
        # regarding which columns are submitted to processing modules
        # or which columns might be targets for ML classification etc

        ignore_columns = data._test_columns + [data._time_column]

        if isinstance(data, DataSource):
            df = data._df
        else:
            df = data

        valid_columns = list(set(df.columns).difference(set(ignore_columns)))

        if self._data_type == "time-series":
            assert data._time_column

            df = df.sort_values(by=data._time_column)

        if data._numeric_columns:
            numeric_columns = data._numeric_columns

        else:
            numeric_columns = [
                col for col in valid_columns if df[col].dtype in _NUMERIC_DTYPES
            ]

        if data._categorical_columns:
            categorical_columns = data._categorical_columns
        else:
            categorical_columns = [
                col
                for col in valid_columns
                if df[col].dtype in _CATEGORICAL_DTYPES and col not in numeric_columns
            ]

        if self._categorical_encoding_limit:
            categorical_columns = [
                col
                for col in categorical_columns
                if df[col].nunique() <= self._categorical_encoding_limit
            ]

        if categorical_columns:
            categorical_df = df[categorical_columns]
            categorical_X = pd.get_dummies(
                categorical_df, # prefix=categorical_df.columns
            ).values

        if numeric_columns:
            numeric_X = df[numeric_columns].values

        if categorical_columns and numeric_columns:
            X = np.concatenate([numeric_X, categorical_X], axis=1)

        elif numeric_columns:
            X = numeric_X
        elif categorical_columns:
            X = categorical_X
        else:
            raise ValueError("No data in dataframe after selecting for valid columns")

        # TODO for e.g missing value imputation and perhaps augmentation we will need to
        # retain the mapping from column names to numpy columns
        mapping = None

        return X, mapping
