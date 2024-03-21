from datetime import datetime
import pandas as pd
from ludwig.utils.data_utils import add_sequence_feature_column
import logging
from ludwig.api import LudwigModel
import matplotlib.pyplot as plt


from ludwig.contribs.mlflow import MlflowCallback
from mage_ai.settings.repo import get_repo_path
import mlflow
from os import path
import yaml
# import mlflow
# import mlflow.pyfunc
import os
import time
import logging
# 
from ludwig.visualize import learning_curves


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
# column_name='flow_urn:ngsi-ld:HydrometricStation:X045631001'




def save_model(model, df,figure_path,figure_path_test):
    class LudwigModel(mlflow.pyfunc.PythonModel):
        def __init__(self, model):
            self.model = model
    
        # def predict(self, context, forecast):
        #     return self.model.forecast(forecast).values
        def predict(self, context, model_input):
            """This is an abstract function, customized it into a method to fetch the Ludwig model."""

            return self.model

    with mlflow.start_run(experiment_id=mlflow.get_experiment_by_name("my_ludwig_experiment").experiment_id) as run:
        mlflow.pyfunc.log_model(artifact_path="ludwig_model", python_model=LudwigModel(model), code_path=None, conda_env=None)

        
        # for k, v in metrics.items():
        #     mlflow.log_params({k: v})

        # for k, v in figures.items():
        #     mlflow.log_figure(v, k)
        mlflow.log_artifact(figure_path, artifact_path="figures")
        mlflow.log_artifact(figure_path_test, artifact_path="figures")

        mlflow.log_dict(df.to_dict(), "dataset_ludwig.csv")
    
    return run.info.run_id
# 

def train_test_split_ludwig(df_new,column_name):
    # split data into train, validation and test->10% test size
    train_size = int(0.7 * len(df_new))
    vali_size = int(0.2 * len(df_new))

    # train, validation, test split
    df_new['split'] = 0
    df_new.loc[
        (
            (df_new.index.values >= train_size) &
            (df_new.index.values < train_size + vali_size)
        ),
        ('split')
    ] = 1
    df_new.loc[
        df_new.index.values >= train_size + vali_size,
        ('split')
    ] = 2

    # prepare timeseries input feature colum
    # (here we are using 20 preceding values to predict the target)
    add_sequence_feature_column(df_new, column_name, 20)
    return df_new

def config_and_train(df_new,column_name):
    # get all temperature columns from dataframe
    temperature_columns = [col for col in df_new.columns if 'temperature' in col.lower()]

    # Assign each name to a separate variable
    temperature_1, temperature_2,temperature_3,temperature_4,temperature_5,temperature_6 = temperature_columns

    

    config = {
    "input_features": [
        {
        "name": f"{column_name}_feature",    # The name of the input column
        "type": "timeseries",     # Data type of the input column
        "encoder": {"type": "rnn", "embedding_size": 32,"state_size":32}
        },
        {
        "name": f"{temperature_1}",    
        "type": "number"    
        },
        {
        "name": f"{temperature_2}",    
        "type": "number"    
        },
        {
        "name": f"{temperature_3}",    
        "type": "number"    
        },
        {
        "name": f"{temperature_4}",    
        "type": "number"    
        },
        {
        "name": f"{temperature_5}",    
        "type": "number"    
        },
        {
        "name": f"{temperature_6}",    
        "type": "number"
        },
    ],
    "output_features": [
        {
        "name": f"{column_name}",
        "type": "number",
        }
    ],
    "trainer": {
        "epochs": 80,
        "learning_rate": 0.0002
    }
    }

    # random_seed=42

    # mlflow_callback = MlflowCallback()
    model = LudwigModel(config,logging_level=logging.INFO)
    # , callbacks=[mlflow_callback]
    # )


    # model = LudwigModel(config)

    

    # model = LudwigModel(config, logging_level=logging.INFO)
    train_stats, preprocessed_data, output_directory = model.train(dataset=df_new,random_seed=40,experiment_name="my_ludwig_experiment")


    figure=learning_curves(train_stats, output_feature_name=column_name,file_format='png',output_directory='image/learning_curves')

    figure_path = "image/learning_curves/learning_curves_combined_loss.png"

    figures = {
        "learning_curves.png": figure
    }
    # metrics={
        # "training":train_stats['training'],
        #  "test":train_stats['test'],
        #  "validation":train_stats['validation'],
        #  }


    # run_id = save_model(model, df_new,metrics)

    test_stats, predictions_test, output_directory = model.evaluate(
      df_new[df_new.split == 1],
      collect_predictions=True,
      collect_overall_stats=True
    )

    y_Test=df_new[column_name][df_new.split == 1]


    y_test = y_Test.tolist()
    y_pred =predictions_test.values.tolist()

    plt.figure()

    plt.scatter(range(len(y_test)), y_test, color='blue', label='Actual (y_test)')
    plt.scatter(range(len(y_pred)), y_pred, color='red', label='Predicted (y_pred)')

    # save scatter plots figure
    plt.xlabel("Data Point")
    plt.ylabel("Values")
    plt.title("Scatter Plot of Actual vs Predicted Values")
    plt.legend()
    figure_path_test = "image/scatter_test_pred.png"

    plt.savefig(figure_path_test)


    # run_id = save_model(model, df_new,figures)
    run_id = save_model(model, df_new,figure_path)

    # run_id=save_model(model, df_new)
    return model

def predict_and_eval(model,df_new):
    predictions, _ = model.predict(dataset=df_new)
    eval_stats, _, _ = model.evaluate(dataset=df_new)
    eval_stats_validation, _, _ = model.evaluate(dataset=df_new[df_new['split']==1])
    eval_stats_test, _, _ = model.evaluate(dataset=df_new[df_new['split']==2])

    print(f"""evaluation on whole dataset {eval_stats}
    \n evaluation on validation dataset {eval_stats_validation} 
    \n evaluation on test dataset {eval_stats_test}""")

    # print(f"model used is {model.model}")
    return predictions


def compare_predictions_actual_data(df_new,predictions,column_name):
    df_comparison=pd.DataFrame()
    df_comparison[f'{column_name}_recorded']=df_new[column_name]

    df_comparison[f'{column_name}_predicted']=predictions
    df_comparison['Time']=df_new['Time']

    df_comparison['split']=df_new['split']
    return df_comparison

def plot_data(df_comparison):
    plt.figure(figsize=(12, 6))
    plt.plot(df_comparison['Time'][df_comparison['split']==2], df_comparison[f'{column_name}_recorded'][df_comparison['split']==2], label='Actual Recorded Data')
    plt.plot(df_comparison['Time'][df_comparison['split']==2], df_comparison[f'{column_name}_predicted'][df_comparison['split']==2], color='red', label='Predictions',marker='o')
    plt.xlabel('Time')
    plt.ylabel('Value')
    plt.xticks(rotation=45)
    plt.legend()
    plt.show()


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

    column_name=kwargs.get('column_name')
    print(f"column_name is {column_name}")

    if column_name is None:
        column_name="flow_urn:ngsi-ld:HydrometricStation:X045631001"
        print(f"column_name is {column_name}")

    temperature_columns = [col for col in data.columns if 'temperature' in col.lower()]


    print(type(data))


    df_new = pd.DataFrame({
        "Time": data["observedAt"],
        column_name: data[column_name],
        **{col: data[col] for col in temperature_columns}

    # temperature_columns : temperature_columns

    })



    df_new=train_test_split_ludwig(df_new,column_name)



    model=config_and_train(df_new,column_name)



    predictions=predict_and_eval(model,df_new)

    df_comparison=compare_predictions_actual_data(df_new,predictions,column_name)

    print(f"df_comparison {df_comparison}")

    return df_comparison


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'