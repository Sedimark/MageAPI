from os import path
import yaml
import openai
from sklearn.model_selection import train_test_split
import pandas as pd
import matplotlib.pyplot as plt
import datetime
from mage_ai.settings.repo import get_repo_path
import os
import mlflow
import numpy as np
import pmdarima
from pmdarima.metrics import smape
from statsmodels.tsa.arima_model import ARIMA


if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter


# config MLFlow env
config_path = path.join(get_repo_path(), 'io_config.yaml')
with open(config_path, "r") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)


MLFLOW_TRACKING_USERNAME = config['default']['MLFLOW_TRACKING_USERNAME']
MLFLOW_TRACKING_PASSWORD = config['default']['MLFLOW_TRACKING_PASSWORD']
AWS_ACCESS_KEY_ID = config['default']['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = config['default']['AWS_SECRET_ACCESS_KEY']
MLFLOW_S3_ENDPOINT_URL = config['default']['MLFLOW_S3_ENDPOINT_URL']
MLFLOW_TRACKING_INSECURE_TLS = config['default']['MLFLOW_TRACKING_INSECURE_TLS']


os.environ['MLFLOW_TRACKING_USERNAME'] = MLFLOW_TRACKING_USERNAME
os.environ['MLFLOW_TRACKING_PASSWORD'] = MLFLOW_TRACKING_PASSWORD
os.environ['AWS_ACCESS_KEY_ID'] = AWS_ACCESS_KEY_ID
os.environ['AWS_SECRET_ACCESS_KEY'] = AWS_SECRET_ACCESS_KEY
os.environ['MLFLOW_S3_ENDPOINT_URL'] = MLFLOW_S3_ENDPOINT_URL
os.environ['MLFLOW_TRACKING_INSECURE_TLS'] = MLFLOW_TRACKING_INSECURE_TLS
os.environ['MLFLOW_HTTP_REQUEST_TIMEOUT'] = "1000"

mlflow.set_tracking_uri("http://62.72.21.79:5000")

def linear_regression_predict(data,model_name):

    X_test=data[1]
    ytest=data[2]

    # get last timestamp
    last_timestamp = X_test[-1]
# 
    print(f"last_timestamp {last_timestamp[0]}")

    # Calculate Unix timestamps for the next 3 days
    next_unix_timestamps = []
    for i in range(1, 4):  # Calculate for the next 3 days
        next_day = datetime.datetime.fromtimestamp(last_timestamp[0]) + datetime.timedelta(days=i)
        next_unix_timestamps.append(int(next_day.timestamp()))

    # next_unix_timestamps now contains the Unix timestamps for the next 3 days
    for ts in next_unix_timestamps:
        X_test.append([ts])
    
    return X_test,ytest,model_name


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

    model_name = data[0]
    print(f"model name :{model_name}")

    X_test,ytest,model_name=linear_regression_predict(data,model_name)


    loaded_model = mlflow.sklearn.load_model(f"models:/{model_name}/1")
    predictions = loaded_model.predict(X_test)


    return X_test,ytest,predictions