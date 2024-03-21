import pandas as pd 
import os
from mage_ai.io.file import FileIO
if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@data_loader
def load_data_from_file(*args, **kwargs):
    """
    Template for loading data from filesystem.
    Load data from 1 file or multiple file directories.

    For multiple directories, use the following:
        FileIO().load(file_directories=['dir_1', 'dir_2'])

    Docs: https://docs.mage.ai/design/data-loading#fileio
    """
    csv_filepath = 'sedimark_demo/data_loaders/input/Humidity-data-23_02_2023 14 57 27 (2023_04_10 07_33_52 UTC).csv'
    # csv_filepath='sedimark_demo/data_loaders/input/Temperature-data-23_02_2023 14 54 17.csv'

    try:
        df=pd.read_csv(csv_filepath)
        file_extension = os.path.splitext(csv_filepath)[1]
        df['humidity'] = df['humidity'].str.replace('%', '').astype(float)
        df_extension = pd.DataFrame({"extension": [file_extension]})

        # Print the DataFrame
        print(df_extension)
        print(df_extension['extension'].iloc[0])

        return [df,df_extension]
    # Specify your data loading logic here
    except FileNotFoundError:
        print('error',FileNotFoundError)
        pass 


# @test
# def test_output(output, *args) -> None:
#     """
#     Template code for testing the output of the block.
#     """
#     assert output is not None, 'The output is undefined'
