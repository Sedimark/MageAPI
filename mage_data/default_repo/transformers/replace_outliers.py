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
    threshold = 3
    if kwargs.get("threshold") is not None:
        threshold = kwargs.get("threshold")

    if kwargs.get("columns") is not None:
        for column in kwargs.get("columns"):
            if pd.api.types.is_numeric_dtype(data[column]):
                mean = np.mean(data[column])
                std = np.std(data[column])
                self.df[column] = data[column].apply(
                    lambda x: np.nan if (np.abs((x - mean) / std) >= threshold) else x)
    else:
        for column in list(data.columns):
            if pd.api.types.is_numeric_dtype(data[column]):
                mean = np.mean(data[column])
                std = np.std(data[column])
                data[column] = data[column].apply(
                    lambda x: np.nan if (np.abs((x - mean) / std) >= threshold) else x)


    return data


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
