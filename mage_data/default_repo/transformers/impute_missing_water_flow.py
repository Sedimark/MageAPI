from dqp.core import DataSource
from dqp.missing import MissingImputationModule
import pandas as pd

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test




def impute_water_flow(df_pivoted):
    # df_columns=['X031001001', 'X050551301','X045401001', 'X051591001']
    # df_columns= ['X051591001', 'X031001001','X045401001', 'X050551301']
    # df_columns= ['X031001001','X045401001', 'X050551301','X045631001','X051591001']

    df_columns = ['X031001001','X045401001','X051591001','X050551301']

    for column in df_columns:
        df_pivoted[column] = pd.to_numeric(df_pivoted[column])
    
    datasource = DataSource(df=df_pivoted)

    methods = MissingImputationModule.list_available_methods()

    # configuration for interpolation-ucd
    config = {'imputation_method': 'Interpolation'}
    module = MissingImputationModule(**config)

    result = module.process(datasource)
    df_result = pd.DataFrame(result._df)

    return df_result

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

    df_result=impute_water_flow(data)
    return df_result


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'