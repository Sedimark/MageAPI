from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from os import path
import yaml

import logging

import os
import time
import lightgbm
import re
import numpy as np
from sklearn.model_selection import TimeSeriesSplit
from lightgbm import LGBMRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from os import path
import yaml
from sklearn.model_selection import train_test_split
import mlflow
import warnings
from mage_ai.settings.repo import get_repo_path
import numpy as np

from sklearn.model_selection import GridSearchCV
from mage_ai.data_preparation.variable_manager import get_variable

# warnings.filterwarnings("ignore")
warnings.filterwarnings( "ignore", module = "matplotlib\..*" )

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

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

def plot_predictions(test_data,y_test,y_pred):
  plt.figure()
  plt.plot(test_data.index,y_test, label='Actual Water Flow')
  plt.plot(test_data.index,y_pred, label='Predicted Water Flow', linestyle='--')
  plt.ylabel('Test Water Flow')
  plt.legend()
  figure_path = "water_flow_model.png"
  plt.savefig(figure_path)
  
#   return plt




def mae_score(y_true,y_pred):
    mae = mean_absolute_error(y_true, y_pred)
    return mae

# def calculate_precision(y_true,y_pred):
#     result=[]
#     cm=[]
#     for i in range (len(y_true)):
#         abs_difference=abs(y_true[i] - y_pred[i])
#         result.append(abs_difference/y_true[i])

#     # cm=confusion_matrix(y_true, y_pred)

#     # print(cm)

#     mean_precision = sum(result) / len(result)
#     # print(f"mean_precision : {mean_precision}")
#     return mean_precision


def calculate_precision(y_true, y_pred):
    result = []
    for i in range(len(y_true)):
        if y_true[i] != 0:
            abs_difference = abs(y_true[i] - y_pred[i])
            result.append(abs_difference / y_true[i])
    if len(result) == 0:
        return np.nan  
    mean_precision = np.mean(result)
    return mean_precision
    

@transformer
def transform(data, *args, **kwargs):
    """
    Template code for a transformer block.

    Add more parameters to this function if this block has multiple parent blocks.
    There should be one parameter for each output variable from each parent block.

    Args:
        data: The output from the upstream parent block
        args: The output from any additional upstream blocks (if applicable)

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """
    # data_precipitation = get_variable('flawless_waterfall', 'load_precipitation', 'output_0')


    df_new=data.copy()

    # df_new = pd.concat([df_new,data_precipitation], axis=1)

    print(df_new.head())

    target_column = 'X050551301'

    # exclude target from input
    features = df_new.drop(columns=[target_column]).columns



    # features=df_new.columns

    print(f'input features: {features}')




    print(f'target column: {target_column}')

    param_grid = {
    'learning_rate': [0.1, 0.3, 0.5],
    'n_estimators': [50, 100, 200],
    'max_depth': [-1],
    }

    # param_grid = {
    #     'learning_rate': [0.01, 0.03, 0.1, 0.3, 1],
    #     'n_estimators': range(50, 501, 50),  # Range of n_estimators
    #     'max_depth': [3, 5, 7],
    #     'num_leaves': range(20, 101, 20),  # Additional hyperparameters
    #     'min_data_in_leaf': range(10, 51, 10),
    #     'feature_fraction': [0.6, 0.8, 1.0],
    #     'reg_alpha': [0.0, 0.1, 1.0]  # Regularization parameters
    # }



    model = GridSearchCV(LGBMRegressor(random_state=None), param_grid=param_grid,  scoring=mae_score)

    # model = LGBMRegressor(learning_rate=0.3)

    train_data, test_data = train_test_split(df_new, test_size=0.2, shuffle=False)


    X_train, y_train = train_data[features], train_data[target_column]
    X_test, y_test = test_data[features], test_data[target_column]

    # Print the training and testing data
    print("Training data:")
    print(train_data)

    print("\nTesting data:")
    print(test_data)
  




    # predictions = []



    model.fit(X_train, y_train)


    
    best_model = model.best_estimator_
    best_params = model.best_params_


    # y_pred = model.predict(X_test)


    y_pred = best_model.predict(X_test)
    mean_precision=calculate_precision(y_test,y_pred)




    mae = np.round(mean_absolute_error(y_test, y_pred), 3)



    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)  # Root Mean Squared Error


    r_squared = r2_score(y_test, y_pred)

    print(f"MAE: {mae}")

    print(f"MSE: {mse}")

    print(f"R-squared: {r_squared}")

    print(f"mean_precision {mean_precision}")
  
    mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100
    print(f"mape_scores: {mape}")

    
    metrics={
            "mse":mse,
            "rmse":rmse,
            "mae":mae,
            "r_squared":r_squared,
            "mape":mape,
            "mean_precision":mean_precision
            }



    y_test.reset_index(drop=True,inplace=True)



    df_compare=pd.DataFrame()
    df_compare['y_pred']=y_pred
    df_compare['y_test']=y_test
    print(f"df_compare {df_compare}")



    plot_predictions(test_data,y_test,y_pred)



    with mlflow.start_run(experiment_id=mlflow.get_experiment_by_name("water_flow").experiment_id) as run:
        # mlflow.pyfunc.log_model(artifact_path="water_flow_model", python_model=LgBoostModel(model), code_path=None, conda_env=None)
        mlflow.sklearn.log_model(
            # sk_model=model,
            sk_model=best_model,

            artifact_path="water_flow_model",


        )

        mlflow.log_artifact("water_flow_model.png", artifact_path="figures")

        for k, v in metrics.items():
            mlflow.log_params({k: v})



    return [df_compare, run_id]









@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'