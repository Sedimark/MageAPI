from datetime import datetime
import logging
import matplotlib.pyplot as plt
from mage_ai.settings.repo import get_repo_path
import mlflow
from os import path
import yaml

import os
import time
import logging
import lightgbm
import re
import numpy as np
import pandas as pd
from sklearn.model_selection import TimeSeriesSplit
from lightgbm import LGBMRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test



# 
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

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


def save_model(model, df,figure_path,metrics):
    class LgBoostModel(mlflow.pyfunc.PythonModel):
        def __init__(self, model):
            self.model = model


        # def predict(self, context, model_input):
        #     """This is an abstract function, customized it into a method to fetch the LGBoost model."""

        #     return self.model
        def predict(self, context, model_input):  
            """Make predictions using the LgBoost model."""  
            
            # Perform forecast on the next 5 days  
            forecast_input = model_input.tail(1)  # Get the last row from the DataFrame as the input for forecasting  
            
            forecast_predictions = []  
            for _ in range(5):  
                prediction = self.model.predict(forecast_input)  
                forecast_predictions.append(prediction)  
                
                # Update the forecast_input for the next day  
                forecast_input = forecast_input.shift(-1)  # Shift the input by one row  
                forecast_input.iloc[-1] = prediction  # Update the last row with the predicted value  
            
            return forecast_predictions  


    with mlflow.start_run(experiment_id=mlflow.get_experiment_by_name("my_lgboost_experiment").experiment_id) as run:
        mlflow.pyfunc.log_model(artifact_path="lgboost_model", python_model=LgBoostModel(model), code_path=None, conda_env=None)


        mlflow.log_artifact(figure_path, artifact_path="figures")
        # mlflow.log_artifact(figure_path_test, artifact_path="figures")
        # mlflow.log_dict(df.to_dict(orient='split'), "dataset_lgboost.csv")  # Use orient='split' to handle mixed data types
        for k, v in metrics.items():
            mlflow.log_params({k: v})
        # mlflow.log_dict(df.to_dict(), "dataset_lgboost.csv")

    return run.info.run_id

@transformer
def transform(df_new, *args, **kwargs):
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
    # Specify your transformation logic here
    column_name=kwargs.get('column_name')
    print(f"column_name is {column_name}")

    if column_name is None:
        column_name="flow_urn:ngsi-ld:HydrometricStation:X045631001"
        print(f"column_name is {column_name}")

    # temperature_columns = [col for col in df_new.columns if 'temperature' in col.lower()]

    # print(temperature_columns)


    # List of columns to exclude
    columns_to_exclude = ['observedAt']
    df_new['new_target'] = df_new[column_name]

    # Get all columns except those in columns_to_exclude
    features = df_new.columns.difference(columns_to_exclude).tolist()
    
    cleaned_features = [re.sub('[^a-zA-Z0-9_]', '_', feature) for feature in features]
    df_new.rename(columns=dict(zip(features, cleaned_features)), inplace=True)

    # adjust df to insert date columns
    df_new['observedAt'] = pd.to_datetime(df_new['observedAt'])

    # Feature engineering
    df_new['day_of_week'] = df_new['observedAt'].dt.dayofweek
    df_new['day_of_year'] = df_new['observedAt'].dt.dayofyear
    df_new['month'] = df_new['observedAt'].dt.month
    df_new['year'] = df_new['observedAt'].dt.year

    # Sort the DataFrame by timestamp
    df_new = df_new.sort_values(by='observedAt').reset_index(drop=True)
    
    # Features and target variable
    target_column = column_name

    model = LGBMRegressor()
        
    # TimeSeriesSplit for time-series cross-validation
    tscv = TimeSeriesSplit(n_splits=8)

    # Initialize lists to store MAE scores and predictions
    mae_scores = []
    predictions = []
    mape_scores=[]

    # Perform time-series cross-validation
    for train_index, test_index in tscv.split(df_new):
        X_train, X_test = df_new.loc[train_index, cleaned_features], df_new.loc[test_index, cleaned_features]
        y_train, y_test = df_new.loc[train_index, 'new_target'], df_new.loc[test_index, 'new_target']

        # print(X_train)

        # Fit the model on the training data
        model.fit(X_train, y_train)

        # print(f"\n X_test: {X_test}")
        # print(f"\n X_test columns: {X_test.columns}")

        # Make predictions on the test data
        y_pred = model.predict(X_test)



        # Evaluate the model using mean absolute error (MAE)
        # mae = mean_absolute_error(y_test, y_pred)

        mae = np.round(mean_absolute_error(y_test, y_pred), 3)     

        mae_scores.append(mae)
        # 
                
        # Calculate MSE
        mse = mean_squared_error(y_test, y_pred)

    
        # Calculate R-squared
        r_squared = r2_score(y_test, y_pred)

        print(f"MAE: {mae}")

        print(f"MSE: {mse}")

        print(f"R-squared: {r_squared}")
        # Calculate Mean Absolute Percentage Error (MAPE)
        mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100
        mape_scores.append(mape)        # 
        print(f"mape_scores: {mape_scores}")
        print(f"mae scores: {mae_scores}")


        # Store predictions for plotting
        predictions.extend(y_pred)
    


    # plot
    plt.figure()

    plt.plot(df_new['observedAt'][test_index], y_test, label='Actual Water Flow')
    plt.plot(df_new['observedAt'][test_index], y_pred, label='Predicted Water Flow', linestyle='--')
    plt.xlabel('Timestamp')
    plt.ylabel('Water Flow')
    plt.legend()
    # plt.show()
    figure_path = "scatter_test_pred_lgboost.png"

    plt.savefig(figure_path)

    metrics={
            "mean mse":np.mean(mae_scores),
            "mse":mse,
            "r_squared":r_squared,
            "mape":mape,
            "mean mape":np.mean(mape_scores)
            }

    # 
    run_id = save_model(model, df_new,figure_path,metrics)
    #


    # Print mean MAE across folds
    print('Mean MAE: %.3f' % np.mean(mae_scores))
    return run_id


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'