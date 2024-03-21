import json
from datetime import datetime
import pandas as pd

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

def process_dataframe(df):
    data = []
    for row in df.values:
        time_str, measurement_str,measurement_unit_str = row
        time = datetime.strptime(time_str, "%d/%m/%Y %H:%M:%S")
        temperature = float(measurement_str)
        data.append({"Time": time.isoformat(), "measurement": temperature})
    return data

def create_ngsild(data, datatype, unitcode,entityType="WeatherObserved"):
    # Create the NGSI-LD entities
    entities = []
    for item in data:
        entity = {
            "id": f"urn:ngsi-ld:{entityType}:{item['Time']}",
            "type": entityType,

            "dateObserved": {
                "type": "Property",
                "value": item['Time']

            },

            datatype: {
                "type": "Property",
                "value": item['measurement'],
                "unitCode": unitcode
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

    datalist=process_dataframe(data)
    ngsi_ld_data = create_ngsild(datalist, "temperature", "CEL")

    return ngsi_ld_data


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
