import pandas as pd

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


@transformer
def transform(df, *args, **kwargs):
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
    df['observedAt'] = pd.to_datetime(df['observedAt'])

    df.set_index('observedAt', inplace=True)

  # Resample the data at 15-minute intervals
    df_resampled = df.resample('15T').asfreq()

  

    datasource = DataSource(df=df_resampled)


    methods=MissingImputationModule.list_available_methods()
    print(f"Imputation methods are: {methods}")

    #configuration for interpolation-ucd
    config = {
        
        'imputation_method':'Interpolation'
        
        
    }
    module=MissingImputationModule(**config)
    result = module.process(datasource)


    df_result = result._df

    df_result['observedAt']=df_result.index

    df_result = df_result.reset_index(drop=True)


   
    df_result['observedAt'] = df_result['observedAt'].dt.strftime('%Y-%m-%dT%H:%M:%SZ')

    return df_result
