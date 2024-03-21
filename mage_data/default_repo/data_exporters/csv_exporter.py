from mage_ai.io.file import FileIO
from pandas import DataFrame
import json
from mage_ai.settings.repo import get_repo_path
from os import path
import sys
import subprocess
import yaml
import io
import urllib3
import json

http = urllib3.PoolManager()

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter


@data_exporter
def export_data_to_minio(data, *args, **kwargs) -> None:
    """
    Template for exporting data to filesystem.

    Docs: https://docs.mage.ai/design/data-loading#fileio
    """

    attributes = [tag.strip().rstrip('.') for tag in args[0].split(',')]
    tags_test = {}

    # Create a dictionary where the keys are 'Attribute' and the values are the attributes
    for attribute in attributes:
        tags_test[attribute] = attribute

    #  Push data to Minio
    with io.BytesIO(json.dumps(data).encode("utf-8")) as fp:
        file_data = fp.read()
        r = http.request(
            'PUT',
            'http://host.docker.internal:8000/put_object/',
            fields={
                'file': file_data,
                'file_name':"temperature_ngsild.jsonld",
                # 'tags': f''
                'tags': json.dumps(tags_test).encode("utf-8")  # Convert the dictionary to JSON and encode it
    #             'tags': b'{"Measurement":"Temperature", "MeasurementUnit":"Celsius","Period":"DateTime"}'


            })
