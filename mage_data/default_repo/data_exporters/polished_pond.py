import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.arima.model import ARIMA
from sklearn.model_selection import train_test_split
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter


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
    df = pd.DataFrame({
        "Time": pd.to_datetime(data["observedAt"]),
        "Temperature": data['temperature']
    })
    df = df.set_index("Time")
    train, test = train_test_split(df, test_size=0.1, shuffle=False)
    model = ARIMA(train, order=(24,0,2))
    results = model.fit()
    plt.plot(train, color='blue', linewidth=5.0)
    plt.plot(results.fittedvalues, color='red')
    plt.close()

    predicted = pd.DataFrame({
        "Time": test.index[:24],
        "Temperature": results.forecast(24).values
    })

    predicted = predicted.set_index("Time")
    plt.plot(test[:24], color='blue', linewidth=2.0)
    plt.plot(predicted, color='red')


