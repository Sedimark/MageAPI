import os
import yaml
import mlflow
import pandas as pd
from mage_ai.settings.repo import get_repo_path

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


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


@transformer
def transform(df, *args, **kwargs):
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
    start_mlflow()

    print(mlflow.get_experiment_by_name("my_lgboost_experiment"))
    experiment_name = 'my_lgboost_experiment'
    run_id = "697618ce9ea343b085cabde55c2b6b56"
    column_name="flow_urn:ngsi-ld:HydrometricStation:X045631001"
    model_name = "lgboost_model"

    if kwargs.get("experiment_name") is not None and kwargs.get("run_id") and kwargs.get("model_name") and kwargs.get("column_name"):
        experiment_name = kwargs.get("experiment_name")
        run_id = kwargs.get("run_id")
        model_name = kwargs.get("model_name")
        column_name=kwargs.get("column_name")
    
    # Get the list of run IDs for the specified experiment
    runs = mlflow.search_runs(experiment_ids=[mlflow.get_experiment_by_name("my_lgboost_experiment").experiment_id])

    # Extract the run IDs
    run_ids = runs['run_id'].tolist()

    # print(run_ids)

    found_id = False
    for run in run_ids:
        if run_id == run:
            found_id = True
            break

    logged_model = f'runs:/{run_id}/lgboost_model'

    print(logged_model)


    if found_id:
        model = mlflow.pyfunc.load_model(logged_model)

        data = df[0]
        data['new_target']=data[column_name]


        data = data.sort_values(by='observedAt').reset_index(drop=True)


        data['observedAt'] = pd.to_datetime(data['observedAt'])

        start_date = data['observedAt'].iloc[-1]

        # Use timedelta to add 4 days to the last observed date+1
        start_date_plus_one_day = start_date + pd.Timedelta(days=1)
        end_date = start_date_plus_one_day + pd.Timedelta(days=4)


        # Create the date range
        date_range = pd.date_range(start=start_date_plus_one_day, end=end_date)
        print(date_range)

        data=data.drop(['observedAt'],axis=1)

        # Reindex the DataFrame
        data = data.reindex(date_range)

        
        # # # Make predictions using the loaded model, for the next 5 days
        predictions = model.predict(data)  
        
        # # # Create a DataFrame with the predictions  
        output_df = pd.DataFrame({'predictions': predictions, "date": date_range}, index=date_range)  

        # # # Print the output DataFrame  
        print(output_df)  
        return [output_df, df[1]]
    

