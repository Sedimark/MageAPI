import requests
import json
import io
import pandas as pd

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@data_loader
def load_data(config, *args, **kwargs):
    """
    Template code for loading data from any source.

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """
    if kwargs['csv_location'] is not None:
        location = kwargs['csv_location']
        url = location.split("\\")[0]
        path = '/'.join(location.split("\\")[1:])

        body = {
            "url": url,
            "dataset_path": path
        }

        response = requests.post(f"{config['default']['MINIO_API']}/get_object", data=json.dumps(body))

        if response.status_code != 200:
            return {}

        response_url = json.loads(response.content.decode('utf-8'))["url"]
        try:
            response = requests.get(response_url)

            if response.status_code != 200:
                return {}

            return pd.read_csv(io.StringIO(response.text))
        except Exception as e:
            print(f"Error fetching data from the server: {str(e)}")
            return {}

    return {}


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
