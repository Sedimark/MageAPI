##Copyright 2023 NUID UCD. All Rights Reserved.

from dqp.core import DataFrame, DataSource
from ..core import DataFrame, DQPInternalModule, DQPModule
from ..dtypes import _NUMERIC_DTYPES, _CATEGORICAL_DTYPES
import pandas as pd
import numpy as np
from pathlib import Path
import datetime
from scipy.stats import iqr, skew, kurtosis
from .utils import (
    Imbalance,
    F1,
    is_categorical,
    SimpleColinearityChecker,
    unalikeability,
)
import warnings
from typing import Union, List, Tuple
from sklearn.preprocessing import LabelEncoder


class DataProfilingModule(DQPModule):
    def __init__(self, measure_overlap=True, measure_colinearity=True, **params):
        super(DataProfilingModule, self).__init__(
            processing_options=["annotate"],
            measure_colinearity=measure_colinearity,
            measure_overlap=measure_overlap,
            **params,
        )

    def _annotate(
        self, result: dict, data: Union[DataFrame, DataSource], raw_data, **kwargs
    ) -> Union[DataFrame, DataSource]:
        (df_profile, column_profiles) = result

        data._description = df_profile
        data._column_profiles = column_profiles
        return data

    def _get_internal_module(self, **params):
        self._internal_module = DataProfiler(**params)

    def _prepare_data(
        self, data: Union[DataFrame, DataSource]
    ) -> Union[DataFrame, DataSource]:
        return data, None

    def _process(self, data: Union[DataFrame, DataSource]) -> dict:
        result = self._internal_module.profile(data)
        return result


class DataProfiler(DQPInternalModule):
    _needs_fit = False
    _is_fit = False

    def __init__(
        self, measure_overlap=True, measure_colinearity=True, **params
    ) -> None:
        self._measure_overlap = measure_overlap
        self._measure_colinearity = measure_colinearity

    def profile(self, df: Union[DataFrame, DataSource]) -> Tuple[dict, dict]:
        whole_df_profile = self._profile_df(df)
        column_profiles = self._profile_columns(df)

        return whole_df_profile, column_profiles

    def _get_numeric_df(self, data: Union[DataFrame, DataSource]) -> DataFrame:
        if isinstance(data, DataSource):
            df = data._df
        else:
            df = data

        if data._numeric_columns:
            df = df[data._numeric_columns]

        else:
            df = df[[col for col in df.columns if df[col].dtype in _NUMERIC_DTYPES]]

        return df

    def _get_colinearity(self, df):
        return SimpleColinearityChecker()(df)

    def _profile_df(self, data: Union[DataFrame, DataSource]) -> dict:
        if isinstance(data, DataSource):
            df = data._df
        else:
            df = data

        num_variables = len(df.columns)
        num_observations = len(df)
        missing_cells = df.isnull().sum().sum()
        percent_missing_cells = missing_cells / (num_variables * num_observations)
        total_size = df.memory_usage().sum() / 1024
        avg_size = total_size / len(df.columns)
        numeric_df = self._get_numeric_df(data)
        correlation = numeric_df.corr()
        colinearity = (
            self._get_colinearity(numeric_df) if self._measure_colinearity else None
        )

        result = {
            "num_variables": num_variables,
            "num_observations": num_observations,
            "missing_cells": missing_cells,
            "percent_missing_cells": percent_missing_cells,
            "total_size": total_size,
            "avg_size": avg_size,
            "correlation": correlation,
            "colinearity": colinearity,
        }

        return result

    def _profile_columns(self, data: Union[DataFrame, DataSource]) -> dict:
        result = {}
        valid_columns = [
            col
            for col in data.columns
            if col not in data._annotation_columns + data._ignore_columns
        ]
        for col in valid_columns:
            result[col] = self._profile_column(col, data)
        return result

    def _profile_column(self, col: str, data: Union[DataFrame, DataSource]) -> dict:
        if isinstance(data, DataSource):
            df = data._df
        else:
            df = data
        col = df[col]
        result = self._process_generic_column(col)

        if col.name == data._time_column:
            if not ((col.dtype is datetime.datetime) or (col.dtype == "<M8[ns]")):
                warnings.warn(
                    f"Specified time column: {col.name}, not in required format. Only generic profiling will be performed."
                )
                return result
            result |= self._process_datetime_column(col, data)

        elif col.dtype == "object":
            result |= self._process_object_column(col, data)

        elif col.dtype in ("int64", "float64", "int16", "int8"):
            result |= self._process_numerical_column(col, data)

        elif col.dtype == "bool":
            result |= self._process_boolean_column(col, data)
        else:
            raise ValueError(f"Unknown column format: {col.dtype}")

        return result

    def _process_generic_column(self, column: pd.Series) -> dict:
        result = {}
        result["name"] = column.name
        result["dtype"] = column.dtype
        result["missing"] = column.isnull().sum()
        result["percent_missing"] = result["missing"] / len(column)
        result["duplicates"] = column.duplicated().sum()
        result["percent_duplicates"] = result["duplicates"] / len(column)
        result["unique"] = column.nunique()
        result["percent_unique"] = result["unique"] / len(column)
        result["memory"] = column.memory_usage() / 1024
        return result

    def compute_overlap(
        self, data: Union[DataFrame, DataSource], column: pd.Series, metric="all"
    ) -> np.array:
        invalid_columns = (
            data._categorical_columns + [column.name] + data._annotation_columns
        )
        if data._time_column:
            invalid_columns.append(data._time_column)

        if isinstance(data, DataSource):
            df = data._df
        else:
            df = data
        X = df[[col for col in data.columns if col not in invalid_columns]]
        y = column
        #y = LabelEncoder().fit_transform(y)
        return F1(X, y)

    def _get_consistency(
        self, col: pd.Series, data: Union[DataFrame, DataSource]
    ) -> float:
        if data._valid_ranges is not None and col.name in data._valid_ranges:
            max = data._valid_ranges[col.name].max
            min = data._valid_ranges[col.name].min
            greater_than = col.values > max
            less_than = col.values < min
            out_of_range = np.logical_or(greater_than, less_than)
            return out_of_range.sum() / len(col)

        else:
            return None

    def _process_numerical_column(
        self, col: pd.Series, data: Union[DataFrame, DataSource]
    ) -> dict:
        result = {
            "min": col.min(),
            "max": col.max(),
            "average": col.mean(),
            "std": col.std(),
            "25%": col.quantile(0.25),
            "50%": col.quantile(0.5),
            "75%": col.quantile(0.75),
            "median": col.median(),
            "histogram": np.histogram(col[~pd.isna(col)].values),
            "consistency": self._get_consistency(col, data),
            "skewness": skew(col),
            "kurtosis": kurtosis(col),
            "mean_absolute_deviation": (col - col.mean()).abs().mean(),
        }

        return result

    def _process_object_column(
        self, col: pd.Series, data: Union[DataFrame, DataSource]
    ) -> dict:
        tmplen = col[~col.isnull()].str.len()
        result = {
            "min_length": min(tmplen),
            "max_length": max(tmplen),
            "average_length": np.mean(tmplen),
            "median_length": np.median(tmplen),
            "histogram": np.histogram(tmplen),
            "label_frequency": col.value_counts(),
        }

        if is_categorical(col):
            result["imbalance"] = Imbalance(metrics="all")(col)
            if self._measure_overlap:
                result["overlap"] = self.compute_overlap(data, col, "all")
            result["unalikeability"] = unalikeability(col)

        return result

    def _process_boolean_column(
        self, col: pd.Series, data: Union[DataFrame, DataSource]
    ) -> dict:
        result = {}
        result["label_frequency"] = col.value_counts()
        result["imbalance"] = Imbalance(metrics="all")(col)
        return result

    def _find_missing(self, diff_col):
        temp = (
            (diff_col / pd.Timedelta(seconds=diff_col.median().total_seconds()))
            .sub(1)
            .fillna(0)
            .astype(int)
        )
        return temp.sum()

    def _process_datetime_column(
        self, col: pd.Series, data: Union[DataFrame, DataSource]
    ) -> dict:
        result = {}

        result["min_date"] = col.min()
        result["max_date"] = col.max()
        # TODO datetimes should be in one format from data loader
        # shouldn't require processing here.
        unit = "seconds"
        col = col.sort_values()
        col_diff = col.diff()
        col_diff = col_diff[~col_diff.isna()]
        col_diff_sec = col_diff.dt.total_seconds()

        result = {
            "date_diff_min": col_diff_sec.min(),
            "date_diff_max": col_diff_sec.max(),
            "date_diff_unit": unit,
            "date_regularity_mean": col_diff_sec.mean(),
            "date_regularity_median": col_diff_sec.median(),
            "date_regularity_iqr": iqr(col_diff_sec),
            "date_regularity_std": np.std(col_diff_sec),
            "histogram": np.histogram(col_diff_sec),
        }

        if result["date_regularity_median"] != 0:
            result["count_missing_based_on_regularity"] = self._find_missing(col_diff)
            result["complete_based_on_regularity"] = len(col) / (
                result["count_missing_based_on_regularity"] + len(col)
            )
        return result
