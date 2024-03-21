import pandas as pd
from dqp.core import DataSource
from dqp.anomaly import AnomalyDetectionModule
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


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

    valid_ranges = []
    numeric_columns = []
    categorical_columns = []

    for column in data.columns:
        if pd.api.types.is_numeric_dtype(data[column]):
            data[column] = data[column].apply(lambda x: float(x))
            numeric_columns.append(column)
            
    data = DataSource(
        data,
        time_column="observedAt",
        valid_ranges=valid_ranges,
        categorical_columns=categorical_columns,
        numeric_columns=numeric_columns,
    )

    config = {
    
        "model" : 'pyod_mcd',
        "processing_options":'describe',
        "model_config" : {
            'threshold_type':'AUCP', 
        },
        "data_type":'tabular'
    }

    plt.rcParams['font.family'] = 'DejaVu Sans Mono'

    module = AnomalyDetectionModule(**config)
    result = module.process(data)
    df = result._df
    df['_is_anomaly'] = df['_is_anomaly'].apply(lambda x: 0 if not x else 1)
    df['_anomaly_score'] = df['_anomaly_score'].apply(lambda x: float(round(x, 2)))
    print("Outliers: ", len(df.loc[df['_is_anomaly'] == True]))
    for ind, col in enumerate(list(df.columns)):
        plt.plot(np.arange(len(df[col])), df[col])
        plt.scatter(np.arange(len(df[col]))[df['_is_anomaly']], df[col][df['_is_anomaly']],c='red')
        plt.title(col)
        plt.show()
    
    return df


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
