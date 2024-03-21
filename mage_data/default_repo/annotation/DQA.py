import pandas as pd
import json
from dqp import AnomalyDetectionModule, DeduplicationModule


# from UC_modules.UC_data_quality_metrics import dq_dimensions
#

def DataQualityAssessment(data):
    """
    Defines a function that assesses the data quality
    Args:
    - data: the entity to be evaluated
    - is_synthetic: boolean indicating whether the entity being assessed has been synthetically created or not
    Returns:
    - data quality
    """
    # DQ_dim = ['accuracy', 'completeness', 'timeliness', 'precision']
    #
    # # DQ_dimensions
    all_dim = []
    # for index, row in data.iterrows():
    #     dimensions, error = dq_dimensions.dq_dimensions(row.to_dict(), bool(row['is_synthetic']), DQ_dim)
    #     all_dim.append(dimensions)
    # all_dim = pd.concat(all_dim, ignore_index=True)
    # Anomaly detection
    config = {
        "model": 'pyod_mcd',
        "processing_options": 'describe',
        "model_config": {
            # 'threshold_type':'contamination', 'threshold_parameters':{'contamination':0.005},
            'threshold_type': 'AUCP',
        },
        "data_type": 'tabular'
        # "data_type":'time-series'
    }
    AD_module = AnomalyDetectionModule(**config)
    AD_result = AD_module.process(data)._df

    # Duplication
    config = {
        "processing_options": 'describe',
        "model_config": {
            "linkage_rules": [
                {
                    "field_1": "observedAt",
                    "field_2": "observedAt",
                    "base_method": "date",
                    "parameters": {},
                }
            ],
            "match_threshold": 2,
            "indexing_method": 'Full',
            "index_column": "observedAt",
        }
    }
    DD_module = DeduplicationModule(**config)


    if not DD_result._df.index.is_unique:
    # Handle duplicate index values here, such as resetting the index
        DD_result._df.reset_index(drop=True, inplace=True)
    
    DD_result = DD_module.process(data)._df

    print(f"AD_result-{AD_result.columns}")
    print(f"DD_result-{DD_result.columns}")

    # DQAssessment
    dataQuality = pd.concat(
        [AD_result['_is_anomaly'], AD_result['_anomaly_score'],
         DD_result['_is_duplicate'], DD_result['_found_matches'],
         data._df['observedAt']
         ], axis=1)

    # [all_dim, AD_result['is_anomaly', 'anomaly_score'], DD_result['is_duplicate', 'found_matches']], axis=1)
    all_dqa = {}

    for index, row in dataQuality.iterrows():
        date = row['observedAt']
        # date = row['dateModified']
        dqa = DataQualityMapping(row, index, date)
        # dqa = DataQualityMapping(row, row['id'], date)
        # dqa = DataQualityMapping(row, "csv", date)
        # all_dqa.update(dqa)
        all_dqa[index] = dqa
    print(f"all_dqa {all_dqa}")
    
    return all_dqa

    


def DataQualityMapping(data, id, date):
    """
    Defines a function that annotates data by creating DataQualityAssessment entity
    Args:
    - data: DataFrame that contains an instance presented by different attributes
    - id: identifier of the entity
    - date: date of the calculated/assessed entity
    Returns:
    - Annotated instance with DQ measures
    """
    # Mapping to the data quality properties
    entity = {
        "id": f"urn:ngsi-ld:DataQualityAssessment:{id}",
        "type": "DataQualityAssessment",
        "dateCalculated": {
            "type": "Property",
            "value": date
        },
        "source": {
            "type": "Property",
            "value": "https://sedimark.eu"
        },
        # "accuracy": {
        #     "type": "Property",
        #     "value": data['accuracy'],
        #     "observedAt": date,
        #     "unitCode": "CEL"
        # },
        # "completeness": {
        #     "type": "Property",
        #     "value": data['completeness'],
        #     "observedAt": date,
        #     "unitCode": "P1"
        # },
        # "timeliness": {
        #     "type": "Property",
        #     "value": data['timeliness'],
        #     "observedAt": date,
        #     "unitCode": "minutes"
        # },
        # "precision": {
        #     "type": "Property",
        #     "value": data['precision'],
        #     "observedAt": date,
        #     "unitCode": "CEL"
        # },
        "outlier": {
            "type": "Property",
            "value": {
                "isOutlier": {
                    "type": "Property",
                    "value": bool(data['_is_anomaly'])
                },
                "outlierScore": {
                    "type": "Property",
                    "value": data['_anomaly_score']
                }
            },
            "observedAt": date
        },
        "duplicate": {
            "type": "Property",
            "value": {
                "isDuplicate": {
                    "type": "Property",
                    "value": bool(data['_is_duplicate'])
                },
                "foundMatches": {
                    "type": "Property",
                    "value": data['_found_matches']
                }
            },
            "observedAt": date
        },
        "@context": [
            "https://raw.githubusercontent.com/smart-data-models/dataModel.DataQuality/master/context.jsonld",
            "https://smartdatamodels.org/context.jsonld"
        ]
    }
    return entity
