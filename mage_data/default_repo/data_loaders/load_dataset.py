import os
import yaml
import requests
import pandas as pd
from mage_ai.settings.repo import get_repo_path

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


def load_config():
    config_path = os.path.join(get_repo_path(), 'io_config.yaml')
    with open(config_path, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    return config


@data_loader
def load_data(*args, **kwargs):
    """
    Template code for loading data from any source.

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """
    config = load_config()
    url = config["default"]["MINIO_API"]

    if kwargs.get("dataset_name") is not None:
        response = requests.get(f"{url}/get_object?dataset_path=datasets{kwargs.get('dataset_name')}&forever=false")

        if response.status_code == 200:
            next_response = requests.get(response.json()["url"])

            if next_response.status_code == 200:
                content = next_response.content.decode('utf-8')

            return pd.read_csv(io.StringIO(content))

    return pd.DataFrame()


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'