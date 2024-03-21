import numpy as np
import os
import io
import yaml
import mlflow
import pandas as pd
from matplotlib import pyplot as plt
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.arima.model import ARIMA
from sklearn.model_selection import train_test_split
from pandas.plotting import register_matplotlib_converters
from mage_ai.settings.repo import get_repo_path
from datetime import datetime
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error, mean_squared_error
register_matplotlib_converters()

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


def load_config():
    config_path = os.path.join(get_repo_path(), 'io_config.yaml')
    with open(config_path, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    os.environ['MLFLOW_TRACKING_USERNAME'] = config['default']['MLFLOW_TRACKING_USERNAME']
    os.environ['MLFLOW_TRACKING_PASSWORD'] = config['default']['MLFLOW_TRACKING_PASSWORD']
    os.environ['AWS_ACCESS_KEY_ID'] = config['default']['AWS_ACCESS_KEY_ID']
    os.environ['AWS_SECRET_ACCESS_KEY'] = config['default']['AWS_SECRET_ACCESS_KEY']
    os.environ['MLFLOW_S3_ENDPOINT_URL'] = config['default']['MLFLOW_S3_ENDPOINT_URL']
    os.environ['MLFLOW_TRACKING_INSECURE_TLS'] = config['default']['MLFLOW_TRACKING_INSECURE_TLS']
    os.environ['MLFLOW_HTTP_REQUEST_TIMEOUT'] = "1000"

    mlflow.set_tracking_uri("http://62.72.21.79:5000")



def save_model(model, df, metrics, figures, forecast_from):
    class ARIMAModel(mlflow.pyfunc.PythonModel):
        def __init__(self, model, forecast_from):
            self.model = model
            self.forecast_from = forecast_from

        def predict(self, context, forecast):
            print(f"This prediction is made from the date: {self.forecast_from}")
            return self.model.forecast(forecast).values


    with mlflow.start_run(experiment_id=mlflow.get_experiment_by_name("status_model").experiment_id) as run:
        mlflow.pyfunc.log_model(artifact_path="arima_model", python_model=ARIMAModel(model, forecast_from), code_path=None, conda_env=None)

        for k, v in metrics.items():
            mlflow.log_params({k: v})


        for k, v in figures.items():
            mlflow.log_figure(v, k)

        mlflow.log_dict(df.to_dict(), "dataset_water.csv")
    
    return run.info.run_id


@transformer
def transform(df_retrieved, *args, **kwargs):
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
    load_config()
    data=df_retrieved[0]
    water_column=df_retrieved[1]
    # print(data[0])
    # print(data[1])

    df = pd.DataFrame({
        "Time": data["observedAt"],
        water_column: data[water_column]
    })

    df_copy = df.copy()
    df["Time"] = pd.to_datetime(df['Time'])

#     df = df.loc[df['Time'] < current_time]
    df = df.set_index("Time")
    train, test = train_test_split(df, test_size=0.2, shuffle=False)
    # acf_original = plot_acf(train)

    # pacf_original = plot_pacf(train)

    # adf_test = adfuller(train)
    # print(f'p-value: {adf_test[1]}')

    # train_diff = train.diff().dropna()
    # train_diff.plot()

    # acf_diff = plot_acf(train_diff)

    # pacf_diff = plot_pacf(train_diff)

    # adf_test = adfuller(train_diff)
    # print(f'p-value: {adf_test[1]}')
    order=(24,1,0)
    model = ARIMA(train, order=order)
    results = model.fit()
    figure, ax = plt.subplots(2, 1, figsize=(8, 8))
    figure.text(0.5, 0.04, 'Time', ha='center')
    figure.text(0.04, 0.5, water_column, va='center', rotation='vertical')
    ax[0].title.set_text('ARIMA Fitted Values')
    ax[0].plot(train, color='blue', linewidth=5.0, label="Train Data")
    ax[0].plot(results.fittedvalues, color='red', label="Fitted Values")

    predicted = pd.DataFrame({
        "Time": test.index,
        water_column: results.forecast(len(test)).values
    })

    predicted = predicted.set_index("Time")
    ax[1].title.set_text('Predictions vs Test')
    ax[1].plot(test, color='blue', linewidth=2.0, label="Test Data")
    ax[1].plot(predicted, color='red', label="Predictions")


    mae = mean_absolute_error(test, predicted)
    mape = mean_absolute_percentage_error(test, predicted)
    rmse = np.sqrt(mean_squared_error(test, predicted))
    metrics = {
        "mae": mae,
        "mape": mape,
        "rmse": rmse,
        "order": order
    }
    figures = {
        "statistic_graph.png": figure,
    }
    print(f"Last index: {train.index[-1]}")
    run_id = save_model(results, df_copy, metrics, figures, train.index[-1])
    print(run_id)

    return run_id


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'