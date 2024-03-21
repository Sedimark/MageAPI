from default_repo.annotation.DQA import DataQualityAssessment
from dqp import core
from dqp.core import DataSource
from dqp import AnomalyDetectionModule, DeduplicationModule

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
    # 
    # data_copy=data.head(2).copy()

    # data_copy.reset_index(drop=True,inplace=True)

    # valid_ranges = []
    # numeric_columns = ['waterFlow']
    # categorical_columns = ['waterStation']

    # data_copy = DataSource(
    #     data_copy,
    #     time_column="observedAt",
    #     valid_ranges=valid_ranges,
    #     categorical_columns=categorical_columns,
    #     numeric_columns=numeric_columns,
    # )
    # # print(data_copy)
    # dqa=DataQualityAssessment(data_copy)
    # print(f"dqa is {dqa}")


    # data=merged_df.copy()

    data_copy=data.tail(1)

    valid_ranges = []
    numeric_columns = ['waterFlow']
    categorical_columns = ['waterStation']

    # print(f"{valid_ranges},CC {categorical_columns}, NC {numeric_columns}")

    data_copy.reset_index(drop=True,inplace=True)
    data_copy = data_copy[~data_copy.index.duplicated()]



    data_copy = DataSource(
        data,
        time_column="observedAt",
        valid_ranges=valid_ranges,
        categorical_columns=categorical_columns,
        numeric_columns=numeric_columns,
    )


    print(f"data_copy {data_copy}")
    dqa=DataQualityAssessment(data_copy)
    print(f"dqa {dqa}")

    # return data


# @test
# def test_output(output, *args) -> None:
#     """
#     Template code for testing the output of the block.
#     """
#     assert output is not None, 'The output is undefined'