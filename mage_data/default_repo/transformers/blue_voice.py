import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from datetime import datetime
from sklearn.model_selection import train_test_split
import numpy as np


if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@transformer
def training_pred(data, *args, **kwargs):
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

    # Create a DataFrame
    df = pd.DataFrame(data)

    # Convert the 'Time' column to datetime format
    df['Time'] = pd.to_datetime(df['Time'], format='%d/%m/%Y %H:%M:%S')

    # Set the 'Time' column as the index
    df.set_index('Time', inplace=True)

    # Split the data into training and test sets
    train_size = int(0.9 * len(df))
    train_data, test_data = df.iloc[:train_size], df.iloc[train_size:]

    # Example values:
    p = 1  # Suggested by PACF
    d = 0  # You may need to adjust this based on stationarity
    q = 1  # Suggested by ACF

    # Create and fit the ARIMA model
    model = ARIMA(train_data['measurement'], order=(p, d, q))

    # Get the model summary
    results = model.fit()
    forecast_steps = len(test_data)
    forecast = results.get_forecast(steps=forecast_steps)
    forecast_values = forecast.predicted_mean
    forecast_ci = forecast.conf_int()
    

    # Print the forecasted values
    print("Forecasted Values:")
    print(forecast_values)


    plt.figure(figsize=(12, 6))
    # plt.plot(train_data['measurement'], label='Training Data',color='green')
    plt.plot(test_data.index, test_data['measurement'], label='Test Data',color='black')
    plt.plot(test_data.index, forecast_values, label='Forecast', color='red')

    plt.title('Temperature Forecast with ARIMA')
    plt.xlabel('Time')
    plt.ylabel('Temperature (°C)')
    plt.legend()
    plt.grid(True)
    plt.show()
