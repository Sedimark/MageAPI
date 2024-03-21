import mlflow
import pandas as pd
import os
import yaml
import mlflow
from ludwig.api import LudwigModel
from mage_ai.settings.repo import get_repo_path
import pandas as pd

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
    
    logged_model = 'runs:/7974058c03234adaaf4536a969bba143/ludwig_model'
    if kwargs.get("logged_model") is not None:
        logged_model = kwargs.get("logged_model")



    # # Load model as a PyFuncModel.
    loaded_model = mlflow.pyfunc.load_model(logged_model)

    # df_new = pd.DataFrame({
        # "flow_urn_ngsi-ld_HydrometricStation_X045631001_feature":[],
        # "feelLikesTemperature # urn_ngsi-ld_Dataset_Open-Meteo":[],
        # 'temperature # urn_ngsi-ld_Dataset_Open-Meteo_2MTR':[],
        # 'soilTemperature # urn_ngsi-ld_Dataset_Open-Meteo_54CMT':[],
        # 'soilTemperature # urn_ngsi-ld_Dataset_Open-Meteo_6CMT':[],
        #  'soilTemperature # urn_ngsi-ld_Dataset_Open-Meteo_18CMT':[],
        #  'soilTemperature # urn_ngsi-ld_Dataset_Open-Meteo_1CMT':[],
        #  'soilTemperature # urn_ngsi-ld_Dataset_Open-Meteo_1CMT':[]
        
    #     # "Time": ['2024-01-18T11:15:00Z']
    #     # 'flow_urn:ngsi-ld:HydrometricStation:X045631001':[]   
    #      })

    data_for_prediction = {
    'observedAt': ['2024-01-18 12:00:00', '2024-01-18 13:00:00', '2024-01-18 14:00:00'],
      "feelLikesTemperature # urn_ngsi-ld_Dataset_Open-Meteo": [25.0, 26.0, 24.5],
      'temperature # urn_ngsi-ld_Dataset_Open-Meteo_2MTR': [23.0, 24.5, 22.0],
     'soilTemperature # urn_ngsi-ld_Dataset_Open-Meteo_54CMT': [15.0, 16.5, 14.0],
    'soilTemperature # urn_ngsi-ld_Dataset_Open-Meteo_6CMT': [18.0, 19.5, 17.0],
     'soilTemperature # urn_ngsi-ld_Dataset_Open-Meteo_18CMT': [20.0, 21.5, 19.0],
   'soilTemperature # urn_ngsi-ld_Dataset_Open-Meteo_1CMT': [22.0, 23.5, 21.0],
     "flow_urn_ngsi-ld_HydrometricStation_X045631001_feature":[40,40,40]
}

    df_for_prediction = pd.DataFrame(data_for_prediction)
     



    # Predict on a Pandas DataFrame.
    predictions=loaded_model.predict(df_for_prediction)
    # predictions=loaded_model.predict(2)

    # # Predict on a Pandas DataFrame.
    # predictions=loaded_model.predict(2)

    print(f"predictions {predictions}")

    # return predictions


# @test
# def test_output(output, *args) -> None:
#     """
#     Template code for testing the output of the block.
#     """
#     assert output is not None, 'The output is undefined'