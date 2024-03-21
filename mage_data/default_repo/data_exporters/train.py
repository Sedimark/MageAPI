import os
import mlflow
import numpy as np
from sklearn.linear_model import LinearRegression
from mage_ai.settings.repo import get_repo_path
from os import path
import yaml
import openai
from sklearn.model_selection import train_test_split
import pandas as pd
import matplotlib.pyplot as plt
import datetime
from statsmodels.tsa.arima.model import ARIMA


if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test



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

mlflow.sklearn.autolog()

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter

def train_linear_regression(data,model_name="temperature_linear_regression",column_name="measurement"):

    data['UnixTime'] = data['Time'].astype(int) // 10**9  # Convert nanoseconds to seconds

    # X and Y features
    X = data[['UnixTime']].values

    y = data[column_name].values

    # Split the data into training (90%) and test (10%) 
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, shuffle=False,random_state=0)

    # train linear regression model
    model = LinearRegression()
    with mlflow.start_run(experiment_id=mlflow.get_experiment_by_name("status_model").experiment_id) as run:
        model.fit(X_train, y_train)
    return model_name, X_test,y_test,run


@data_exporter
def export_train(data, *args, **kwargs) -> None:

    model_name=kwargs.get('model_name')
    print(f"model name is {model_name}")

    column_name=kwargs.get('column_name')
    print(f"column name is {column_name}")
    time_column=kwargs.get('time_column')

    if model_name is None:
        model_name="temperature_test"
        print(f"model name is {model_name}")


    if column_name is None:
        column_name="temperature"
        print(f"column name is {column_name}")
        
    if time_column is None:
        time_column="observedAt"
        print(f"time column is {time_column}")

    data['Time'] = pd.to_datetime(data[time_column])

    model_name, X_test,y_test,run=train_linear_regression(data,model_name=model_name,column_name=column_name)

    run_id = run.info.run_id
    model_uri = f"runs:/{run_id}/model"

    mlflow.register_model(f"runs:/{run_id}/model", model_name, await_registration_for=10)
    print(f"model_name {model_name}")
    return model_name, X_test,y_test
