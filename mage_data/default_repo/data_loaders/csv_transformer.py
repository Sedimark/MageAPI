import json
from datetime import datetime
import pandas as pd

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

def process_dataframe(df):
    data=[]
    for row in df.values:
        time_str, temperature_str = row
        time = datetime.strptime(time_str, "%d/%m/%Y %H:%M:%S")
        temperature = float(temperature_str.split()[0])
        data.append({"Time": time.isoformat(), "temperature": temperature})
    return data

def create_ngsild(data):
    # Create the NGSI-LD entities
    entities = []
    for item in data:
        entity = {
            "id": f"urn:ngsi-ld:Temperature:{item['Time']}",
            "type": "Temperature",
            "observedAt": {
                "type": "DateTime",
                "value": item['Time']
            },
            "temperature": {
                "type": "Property",
                "value": item['temperature'],
                "unitCode": "CEL"
            }
        }
        entities.append(entity)
    return entities

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
    # Specify your transformation logic here
    # print(data.head())
    datalist=process_dataframe(data)
    ngsi_ld_data=create_ngsild(datalist)
    return ngsi_ld_data


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
