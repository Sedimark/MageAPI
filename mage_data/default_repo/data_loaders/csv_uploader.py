from mage_ai.io.file import FileIO
import requests
import pandas as pd
if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@data_loader
def load_data_from_file(config, *args, **kwargs):
    """
    Template for loading data from filesystem.
    Load data from 1 file or multiple file directories.
    For multiple directories, use the following:
        FileIO().load(file_directories=['dir_1', 'dir_2'])

    Docs: https://docs.mage.ai/design/data-loading#fileio
    """

    if kwargs.get("location") is not None:
        location = kwargs["location"]

        url = location.split("=")[0]
        dataset_path = '/'.join(location.split("=")[1:])

        response = requests.post(config["default"]["MINIO_API"], data=json.dumps({
            "url": url,
            "dataset_path": dataset_path
        }))

        if response.status_code != 200:
            return None
        
        body = json.loads(response.content.decode('utf-8'))

        url = body["url"]

        return pd.read_csv(url)

    return None


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'