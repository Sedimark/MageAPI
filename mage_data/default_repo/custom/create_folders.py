import os

if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@custom
def transform_custom():
    """
    Args:
        data: The output from the upstream parent block (if applicable)
        args: The output from any additional upstream blocks

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """
    
    # create output folder
    base_folder='demo/data_exporters'
    output_folder='output'

    output_path = os.path.join(base_folder, output_folder)
    if not os.path.exists(output_path):
        os.makedirs(output_path, exist_ok=True)
        print(f"Created {output_path}")
    else:
        print(f"{output_path} already exists")



# @test
# def test_output(output, *args) -> None:
#     """
#     Template code for testing the output of the block.
#     """
#     assert output is not None, 'The output is undefined'
