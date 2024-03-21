from mage_ai.data_preparation.variable_manager import get_variable
import pandas as pd
from datetime import datetime
from sklearn.model_selection import train_test_split
from sedimark.sedimark_demo import secret
from sedimark.sedimark_demo import connector
import copy
import json
import requests

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter

def convert_numbers(data):
    if isinstance(data, dict):
        return {k: convert_numbers(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_numbers(item) for item in data]
    elif isinstance(data, (int, float)):
        return int(data) if data == int(data) else float(data)
    return data
     
def export_to_broker(data, entity_id = None):
    if entity_id is None:
        entity_id = 'urn:ngsi-ld:WeatherInformation:Forecasted:Hourly:France:Les_Orres-Annotated-Anomaly-UCD'
    print(entity_id)
    bucket ={'host': 'https://stellio-dev.eglobalmark.com',
    'url_keycloak': 'https://sso.eglobalmark.com/auth/realms/sedimark/protocol/openid-connect/token',
    'client_id': secret.client_id,
    'client_secret': secret.client_secret,
    'username': secret.username,
    'password': secret.password,
    'entity_to_load_from': 'urn:ngsi-ld:WeatherInformation:Forecasted:Hourly:France:Les_Orres',
    'entity_to_save_in': entity_id,
    'entitiy_id': entity_id,
    'link_context': 'https://easy-global-market.github.io/ngsild-api-data-models/sedimark/jsonld-contexts/sedimark.jsonld',
    'tenant': 'urn:ngsi-ld:tenant:sedimark',
    'time_query': 'timerel=after&timeAt=2023-08-01T00:00:00Z',
    'content_type': 'application/json'
    }

    stellio_dev = connector.DataStore_NGSILD(bucket['host'], bucket['url_keycloak'])
    stellio_dev.getToken(bucket['client_id'], bucket['client_secret'], bucket['username'], bucket['password'])

    
    load_data = connector.LoadData_NGSILD(data_store=stellio_dev, entity_id=bucket['entity_to_load_from'], context=bucket['link_context'], tenant="urn:ngsi-ld:tenant:sedimark")
    load_data.run(bucket)

    bucket['processed_contextual_data'] = copy.deepcopy(bucket['contextual_data'])

    bucket['processed_temporal_data'] = bucket['temporal_data'].copy()

    # Convert the pandas Series to a Python list
    is_anomaly = data['_is_anomaly'].tolist()
    anomaly_scores = data['_anomaly_score'].tolist()

    # # # Assign the Python list to the JSON-serializable field
    bucket['processed_temporal_data']['is_anomaly'] = is_anomaly
    bucket['processed_temporal_data']['anomaly_scores'] = anomaly_scores
    bucket['entity_id'] = bucket['entity_to_save_in']

    # print(bucket['processed_temporal_data'])
    data_types = bucket['processed_temporal_data'].dtypes
    int64_columns = data_types[data_types == 'int64'].index
    for col in int64_columns:
        bucket['processed_temporal_data'][col] =  bucket['processed_temporal_data'][col].astype(float)

    save_data = connector.SaveData_NGSILD(data_store=stellio_dev, entity_id=bucket['entity_to_save_in'], context=bucket['link_context'], tenant=bucket['tenant'])
    save_data.run(bucket)

@data_exporter
def export_data(data, *args, **kwargs):
    """
    Exports data to some source.

    Args:
        data: The output from the upstream parent block
        args: The output from any additional upstream blocks (if applicable)

    Output (optional):
        Optionally return any object and it'll be logged and
        displayed when inspecting the block run.
    """

    if kwargs.get("save_name") is not None: 
        export_to_broker(data, kwargs.get("save_name"))
    else:
        export_to_broker(data)
