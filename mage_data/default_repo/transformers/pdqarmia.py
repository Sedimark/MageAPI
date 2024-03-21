import pmdarima as pm
import pandas as pd
from sklearn.model_selection import train_test_split
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


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
    df = pd.DataFrame({
        "Time": data["observedAt"],
        "Temperature": data['temperature']
    })
    df_copy = df.copy()
    df["Time"] = pd.to_datetime(df['Time'])
    current_time = datetime.now(df['Time'].dt.tz)

    df = df.loc[df['Time'] < current_time]
    df = df.set_index("Time")
    train, test = train_test_split(df, test_size=0.1, shuffle=False)

    # Fit your model
    model = pm.auto_arima(train, seasonal=True, m=12)
    print("Here")

    # make your forecasts
    forecasts = model.predict(test.shape[0])  # predict N steps into the future

    # Visualize the forecasts (blue=train, green=forecasts)
    x = np.arange(y.shape[0])
    plt.plot(x[:150], train, c='blue')
    plt.plot(x[150:], forecasts, c='green')

    return {}


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'