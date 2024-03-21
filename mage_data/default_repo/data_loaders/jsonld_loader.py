import json

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@data_loader
def load_data(*args, **kwargs):
    """
    Template code for loading data from any source.

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """
    # Specify your data loading logic here
    jsonld_filepath='sedimark_demo/data_loaders/input/dataset_SDR_example.jsonld'
    try:
        with open(jsonld_filepath, 'r') as file:
            # Load the contents of the file
            jsonld_data = json.load(file)
            # print(jsonld_data)
            return jsonld_data

    except FileNotFoundError:
        pass


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
