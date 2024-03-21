from datetime import datetime
import pandas as pd
from ludwig.utils.data_utils import add_sequence_feature_column
import logging
from ludwig.api import LudwigModel
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from os import path
import yaml
from sklearn.model_selection import train_test_split
import numpy as np
if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test



# ***********************************

def mae_score(y_true,y_pred):
    mae = mean_absolute_error(y_true, y_pred)
    return mae

def calculate_precision(y_true, y_pred):
    result = []
    for i in range(len(y_true)):
        if i < len(y_pred) and y_true[i] != 0:
            abs_difference = abs(y_true[i] - y_pred.values[i][0])  # Access value from DataFrame using .values
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

    df_new=data.copy()

    target_column = 'X050551301'

    # exclude target from input
    features = df_new.drop(columns=[target_column]).columns

    print(f'input features: {features}')

    print(f'target column: {target_column}')

    config = {
    "input_features": [
        {
        "name": "X031001001",
        "type": "timeseries",
        },
              {
        "name": "X045401001",
        "type": "timeseries",
        },
              {
        "name": "X051591001",
        "type": "timeseries",
        },

    ],
    "output_features": [
        {
        "name": "X050551301",
        "type": "number",
        }
    ],
        "preprocessing": {
        "scaler": "standard"
    },

    # ###########################
         "training": {
        "epochs": 100, 
        "learning_rate": 0.003,
        },

          "validation_field": "X050551301",
              "validation_metric": "r2",
    "model": {
        "type": "stacked_lstm",  # Changed model type to stacked LSTM for capturing temporal dependencies

    }

    # "trainer": {
    #     "epochs": 50,
    #     "learning_rate": 0.0002,
    # }
    }

    model = LudwigModel(config, logging_level=logging.INFO)

    train_data, test_data = train_test_split(df_new, test_size=0.2, shuffle=False)


    X_train, y_train = train_data[features], train_data[target_column]
    X_test, y_test = test_data[features], test_data[target_column]

    train_stats, preprocessed_data, output_directory = model.train(training_set=train_data, test_set=test_data,
    
        )



    y_pred, _ = model.predict(dataset=test_data)
    eval_stats_test, _, _ = model.evaluate(dataset=test_data)




    mean_precision=calculate_precision(y_test,y_pred)




    mae = np.round(mean_absolute_error(y_test, y_pred), 3)



    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)  # Root Mean Squared Error


    r_squared = r2_score(y_test, y_pred)

    print(f"MAE: {mae}")

    print(f"MSE: {mse}")

    print(f"R-squared: {r_squared}")

    print(f"mean_precision {mean_precision}")


    
    metrics={
            "mse":mse,
            "rmse":rmse,
            "mae":mae,
            "r_squared":r_squared,
            # "mape":mape,
            "mean_precision":mean_precision
            }

    print(f"""\n evaluation on test dataset {eval_stats_test}""")

    df_comparison=pd.DataFrame()

    y_pred.reset_index(drop=True,inplace=True)

    df_comparison[f'{target_column}_recorded']=test_data[target_column]#df_new[column_name]


    y_pred.columns = ['X050551301_predictions']


    df_comparison[f'{target_column}_predicted']=y_pred['X050551301_predictions'].values
    return df_comparison




# @test
# def test_output(output, *args) -> None:
#     """
#     Template code for testing the output of the block.
#     """
#     assert output is not None, 'The output is undefined'