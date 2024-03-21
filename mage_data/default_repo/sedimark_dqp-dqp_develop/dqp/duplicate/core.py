##Copyright 2023 NUID UCD. All Rights Reserved.


from ..core import DQPInternalModule, DQPModule, DataFrame, DataSource
import numpy as np
import pandas as pd
import warnings
from typing import Union, List, Tuple
from collections import defaultdict
import warnings
import tempfile
import json
import recordlinkage
import logging


class RecordLinkageInternalModule(DQPInternalModule):
    def __init__(
        self,
        linkage_rules=[],
        match_threshold=2,
        indexing_method="Full",
        index_column=None,
        **params,
    ):
        self._linkage_rules = linkage_rules
        self._match_threshold = match_threshold
        self._indexing_method = indexing_method
        self._index_on_column = index_column

    def process(self, df: DataFrame) -> Tuple[List[List], np.ndarray]:
        self.indexer = recordlinkage.Index()

        
        if self._indexing_method in ['Block', 'Neighbourhood']:
                  assert (
                self._index_on_column and self._index_on_column in df.columns
            ), "Index colum must be specified for Block or Neighbourhood based indexing"
        
        if self._indexing_method == "Block":
      
            self.indexer.block(self._index_on_column)

        elif self._indexing_method == "Neighbourhood":
        
            self.indexer.sortedneighbourhood(self._index_on_column)

        else:
            self.indexer.full()

        candidate_links = self.indexer.index(df)
        self.compare_cl = recordlinkage.Compare()

        labels = []
        for rule in self._linkage_rules:
            label = self._process_rule(self.compare_cl, **rule)
            labels.append(label)

        features = self.compare_cl.compute(candidate_links, df)
        matches = features[features.sum(axis=1) >= self._match_threshold]
        matched = [[] for i in range(len(df))]
        is_duplicate = np.zeros(len(df))
        for pair in matches.index:
            matched[pair[0]].append(pair[1])
            matched[pair[1]].append(pair[0])
            is_duplicate[pair[1]] = 1

        return matched, is_duplicate > 0

    def _process_rule(self, compare_cl: recordlinkage.Compare, field_1:str=None, field_2:str=None, base_method:str =None, parameters:dict={}) -> None:
        
        assert field_1 and field_2 and base_method, 'Field 1, 2 and a base method must be specified for a dedpulication rule'
        
        label = field_1 + "_" + field_2 + "_" + base_method
    
        methods_dict = {
            'string':compare_cl.string,
            'exact':compare_cl.exact,
            'numeric':compare_cl.numeric,
            'geo':compare_cl.geo,
            'date':compare_cl.date
        }
        
        assert base_method in methods_dict, 'Unknown base_method {base_method}\n'
        
        method = methods_dict[base_method]
        method(field_1, field_2, **parameters)
        
        return label

class DeduplicationModule(DQPModule):
    def __init__(self, processing_options=["describe"], **params):
        super(DeduplicationModule, self).__init__(
            processing_options=processing_options, **params
        )

    def _set_data_params(self, deduplication_fields=[], **params):
        super()._set_data_params(**params)
        self._deduplication_fields = deduplication_fields

    def _get_internal_module(self, model_config={}, **params) -> None:
        
        self._internal_module = RecordLinkageInternalModule(**model_config)
    
    def _prepare_data(self, data:Union[DataFrame, DataSource]) -> Union[DataFrame, DataSource]:
        
        if isinstance(data, DataSource):
            df=data._df
        else:
            df=data
            
        return df, None

    def process(self, data: Union[DataFrame, DataSource]) -> Union[DataFrame,DataSource]:
        raw_data, mapping = self._prepare_data(data)
        self._validate_data(raw_data)
        result = self._process(raw_data)
        data = self._handle_result(result, data, raw_data)
        return data

    def _process(self, data):
        return self._internal_module.process(data)

    def _describe(
        self, result:Tuple, data: Union[DataFrame, DataSource], raw_data
    ) -> Union[DataFrame, DataSource]:
        (matched, is_duplicate) = result

        if isinstance(data, DataSource):
            df = data._df
        else:
            df = data

        df["_found_matches"] = matched
        df["_is_duplicate"] = is_duplicate
        data._annotation_columns.extend(['_found_matches', '_is_duplicate'])
        return data

    def _remove(
        self, result: Tuple, data: Union[DataFrame, DataSource], raw_data
    ) -> Union[DataFrame, DataSource]:
        (_, is_duplicate) = result

        if isinstance(data, DataSource):
            data._df = data._df[~is_duplicate]
            return data
        else:
            return data[~is_duplicate]

       