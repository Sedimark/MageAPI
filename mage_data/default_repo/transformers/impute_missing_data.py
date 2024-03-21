from datetime import datetime
import pandas as pd
import logging
import matplotlib.pyplot as plt
from mage_ai.data_preparation.variable_manager import get_variable
from sedimark.sedimark_dqp.dqp.core import DataSource
# from dqp.core import DataSource
# from dqp.missing import MissingImputationModule
from sedimark.sedimark_dqp.dqp.missing import MissingImputationModule


if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test



# column_name='flow_urn:ngsi-ld:HydrometricStation:X045631001'



def impute_temperatures(merged_df):
    # impute missing temperature data

    datasource = DataSource(df=merged_df)


    methods=MissingImputationModule.list_available_methods()
    print(f"Imputation methods are: {methods}")

    #configuration for interpolation-ucd
    config = {
        
        'imputation_method':'Interpolation'
        
        
    }
    module=MissingImputationModule(**config)
    result = module.process(datasource)


    df_result = result._df


    return df_result


@transformer
def transform(df_temperature, *args, **kwargs):
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


    df_water_stations = get_variable('ml_flow', 'impute_missing_data_ucd', 'output_0')
    df_water_stations=df_water_stations[['observedAt',f'{column_name}']]

    print(f"len water station {len(df_water_stations)}")
    print(f"len temperature {len(df_temperature)}")


    merged_df = df_water_stations.merge(df_temperature, on='observedAt', how='outer')

    # merged_df = df_water_stations.merge(df_temperature, on='observedAt', how='inner') #to do if impute_missing_temperature is used

    df_result=impute_temperatures(merged_df)

    print(type(df_result))

    return df_result
