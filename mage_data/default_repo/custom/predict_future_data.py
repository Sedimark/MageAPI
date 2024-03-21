# from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mage_ai.data_preparation.variable_manager import get_variable
import os
import yaml
import mlflow
from mage_ai.settings.repo import get_repo_path
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

def plot_test_data(df_compare):
    df_compare.plot(kind='scatter', x='y_pred', y='y_test', s=32, alpha=.8)
    plt.gca().spines[['top', 'right',]].set_visible(False)

    plt.xlabel('Predicted Values')
    plt.ylabel('Actual Values')
    plt.title('Comparison between Predicted and Actual Values')



def simulate_future_data(df, periods=30):
    """
    Simulates future data for the next 'periods' days based on the average change observed
    in the most recent data points of the dataset.

    Args:
    df (pd.DataFrame): The original dataset.
    periods (int): Number of future periods to simulate data for.

    Returns:
    pd.DataFrame: A DataFrame containing simulated future data.
    """

    df.index = pd.to_datetime(df.index)


    future_dates = pd.date_range(start=df.index.max(), periods=periods + 1)[1:]
    future_df = pd.DataFrame(index=future_dates)

    change_columns = df.columns#['X031001001', 'X050551301', 'X051591001','rain (mm)']
    recent_df = df[change_columns].tail(7)
    daily_change = recent_df.diff().mean()

    for col in change_columns:
        future_df[col] = df[col].iloc[-1] + daily_change[col] * np.arange(1, periods + 1)

    return future_df#.reset_index().rename(columns={'index': 'observedAt'})



def start_mlflow():
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

@custom
def transform_custom(compare_df, **kwargs):
    """
    args: The output from any upstream parent blocks (if applicable)

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """

    print(compare_df[1])
    data = get_variable('flawless_waterfall', 'impute_missing_water_flow', 'output_0')
    data_precipitation = get_variable('flawless_waterfall', 'load_precipitation', 'output_0')

    data = pd.concat([data,data_precipitation], axis=1)
    print(data.head())


    future_data = simulate_future_data(data,periods=20)
    # print(future_data.index)
    print(f"future data-head {future_data.head()}")

    X_test=future_data
    y_test=future_data['X050551301']


    start_mlflow()

    print(mlflow.get_experiment_by_name("water_flow"))


    # run_id="50fa9a0354d541cd8e42fb76b1e5e315"
    run_id=compare_df[1]

    logged_model = f'runs:/{run_id}/water_flow_model'
    loaded_model = mlflow.pyfunc.load_model(logged_model)


    print(logged_model)

    # logged_model = f'runs:/{run_id}/water_flow_model'

    model = mlflow.pyfunc.load_model(logged_model)


    y_pred = model.predict(X_test)



    mae = mean_absolute_error(y_test, y_pred)

    mae = np.round(mean_absolute_error(y_test, y_pred), 3)

    mse = mean_squared_error(y_test, y_pred)

    r_squared = r2_score(y_test, y_pred)

    print(f"MAE: {mae}")

    print(f"MSE: {mse}")

    print(f"R-squared: {r_squared}")

    mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100
    print(f"mape_scores: {mape}")


    y_test.reset_index(drop=True,inplace=True)



    df_compare=pd.DataFrame()
    df_compare['date']=future_data.index
    df_compare['X050551301_predicted_flow']=y_pred
    print(f"df_compare\n {df_compare}")




    # plot
    # plot_test_data(df_compare)

    # return future_data


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
