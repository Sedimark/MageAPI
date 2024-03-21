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

def calculate_accuracy(df,predictions):
    train, test = train_test_split(df, test_size=0.013, shuffle=False)
    test['TempPredictions']=predictions

    #summing up predictions->calculate mean
    predictions_sum = test['TempPredictions'].sum()
    predictions_mean=predictions_sum/len(predictions)

    predictions_mean_abs=abs(predictions_mean)
    test_sum=test['Temperature'].sum()
    test_mean_abs=abs(test_sum/len(test))

    prediction_test_raport=predictions_mean_abs/test_mean_abs
    accuracy=100-prediction_test_raport
    print(f"accuracy for test values only: {accuracy:.2f}%")

    #accuracy for the entire dataset
    df_sum=df['Temperature'].sum()
    df_mean_abs=abs(df_sum/len(df))

    prediction_df_raport=predictions_mean_abs/df_mean_abs
    accuracy_df=100-prediction_df_raport
    print(f"accuracy for the entire dataset: {accuracy_df:.2f}%")
    # print(f"test dataset and predictions: \n {test}")
    return test
     
def export_to_broker(data):
    bucket ={'host': 'https://stellio-dev.eglobalmark.com',
    'url_keycloak': 'https://sso.eglobalmark.com/auth/realms/sedimark/protocol/openid-connect/token',
    'client_id': secret.client_id,
    'client_secret': secret.client_secret,
    'username': secret.username,
    'password': secret.password,
    'entity_to_load_from': 'urn:ngsi-ld:WeatherInformation:Forecasted:Hourly:France:Les_Orres',
    'entity_to_save_in': 'urn:ngsi-ld:WeatherInformation:Forecasted:Hourly:France:Les_Orres-Temperature-Predictions-Arima',
    'link_context': 'https://raw.githubusercontent.com/easy-global-market/ngsild-api-data-models/master/sedimark/jsonld-contexts/sedimark.jsonld',
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
    # bucket['processed_temporal_data']['tempPredictions']=data['tempPredictions']

    # Convert the pandas Series to a Python list
    temp_predictions_list = data['tempPredictions'].tolist()

    # # # Assign the Python list to the JSON-serializable field
    bucket['processed_temporal_data']['tempPredictions'] = temp_predictions_list

    print(f"predictions  {bucket['processed_temporal_data']['tempPredictions']}")
    print(f"temperature {bucket['processed_temporal_data']['temperature']}")

    print('\Save predictions to broker\n')
    # print(bucket['processed_temporal_data'].keys())


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
    predictions=data

    data = get_variable('train_pipeline', 'load_from_broker', 'output_0')
    
    df = pd.DataFrame({
        "Time": data["observedAt"],
        "Temperature": data['temperature']
    })
    
    df["Time"] = pd.to_datetime(df['Time'])

    test=calculate_accuracy(df,predictions)

    df['tempPredictions']=""
    df['tempPredictions'][-len(test):]=predictions

    # export_to_broker(df)

    return test

