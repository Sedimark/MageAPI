
# from sedimark.dqp.core import DataSource
# from sedimark.dqp.missing import MissingImputationModule


from dqp.core import DataSource
from dqp.missing import MissingImputationModule


import numpy as np
import pandas as pd
# from sedimark.sedimark_dqp.dqp.core import DataSource
from datetime import datetime, timedelta

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


def create_future_timestamps(df_result):

    last_observedAt=df_result['observedAt'].iloc[-1]
    
    # start timestamp-last index
    start_timestamp = datetime.strptime(last_observedAt, '%Y-%m-%dT%H:%M:%SZ')

    print(f"last observed timestamp is {last_observedAt} and the start timestamp is {start_timestamp}")

    # number of timestamps in the future
    num_timestamps = 3  

    # interval between timestamps- 15 mins
    time_interval = timedelta(minutes=15)  

    # Move to the next hour
    start_timestamp += time_interval

    # Generate future timestamps
    timestamps = [start_timestamp + i * time_interval for i in range(num_timestamps)]

    # Convert timestamps to string in the desired format
    timestamps_str = [timestamp.strftime('%Y-%m-%dT%H:%M:%SZ') for timestamp in timestamps]

    # Create a pandas DataFrame with the timestamps
    dfTime = pd.DataFrame({'observedAt': timestamps_str})


    # copy last three
    columns_to_copy = df_result.columns.difference(['observedAt'])

    last_three_values = df_result[columns_to_copy].tail(3)
    # print(f"last three values {last_three_values}")
    last_three_values['observedAt'] = timestamps_str

    df_future = pd.concat([df_result, last_three_values])


    # Reset the index of the DataFrame if needed
    df_future.reset_index(drop=True, inplace=True)
    return df_future



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

    df=data[0]


    datasource = DataSource(df=df)


    methods=MissingImputationModule.list_available_methods()
    print(f"Imputation methods are: {methods}")

    #Define configuration

    config = {
        
        'imputation_method':'Interpolation'
        
        
    }
    module=MissingImputationModule(**config)
    result = module.process(datasource)


    df_result = result._df

    df_future=create_future_timestamps(df_result)

    return df_future

