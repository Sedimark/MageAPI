import pandas as pd
import requests

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
    # csv_filepath='sedimark_demo/data_loaders/input/Temperature-data-23_02_2023 14 54 17.csv'
    # csv_filepath='sedimark_demo/data_loaders/input/Illuminance-data-23_02_2023 14 57 39.csv'
    # csv_filepath='sedimark_demo/data_loaders/input/Humidity-data-23_02_2023 14 57 27.csv'
    # csv_filepath='sedimark_demo/data_loaders/input/precipitation accumulation index-data-23_02_2023 14 57 56.csv'
    # csv_filepath='sedimark_demo/data_loaders/input/Wind Speed AVG-data-23_02_2023 14 58 04.csv'
    # csv_filepath='sedimark_demo/data_loaders/input/Wind Speed Gust-data-23_02_2023 14 58 14.csv'
    # csv_filepath='sedimark_demo/data_loaders/input/Flow-data.csv'
    csv_filepath='sedimark_demo/data_loaders/input/temporal_data_broker.csv'

    server_url = "http://host.docker.internal:8080"  # clean data API


    csv_filepath_mean='sedimark_demo/data_loaders/input/dataset_mean.csv'


    with open(csv_filepath_mean, "rb") as file:
        file_content = file.read()

    # make mean of data
    payload = {"file": ("dataset_mean.csv", file_content, "multipart/form-data")}

    # Make the POST request to mean endpoint
    response = requests.post(f"{server_url}/mean", files=payload)

    
    # Check the response of the means endpoint
    if response.status_code == 200:
        data = response.json()
        print("Message:", data["message"])
        print("Means:")
        for column, mean in data["means"].items():
            print(f"{column}: {mean}")
    else:
        print("Error:", response.status_code)
        print(response.text)



    with open(csv_filepath, "rb") as csv_file:
        # Prepare the POST request with the file as payload
        files = {'file': ('data.csv', csv_file)}

        # Make the POST request to the "/clean" endpoint
        response = requests.post(f"{server_url}/clean", files=files)

        # Check the response
        if response.status_code == 200:
            data = response.json()
            print("Message:", data["message"])
            cleaned_df_req = data.get("cleaned_df")  # Use .get() to handle missing keys
            if cleaned_df_req:
                cleaned_df = pd.read_json(cleaned_df_req)
                return cleaned_df
            else:
                print("No cleaned_df data found in the response.")
        else:
            print("Request to /clean failed with status code:", response.status_code)
            print("Response content:", response.content)


    with open(csv_filepath, "rb") as csv_file:
        # Prepare the POST request with the file as payload
        files = {'file': ('data.csv', csv_file)}

        # Make the POST request to the "/clean" endpoint
        response = requests.post(f"{server_url}/clean/v2", files=files)

        # Check the response
        if response.status_code == 200:
            data = response.json()
            print("Message:", data["message"])
            cleaned_df_req = data.get("cleaned_df") 
            if cleaned_df_req:
                cleaned_df = pd.read_json(cleaned_df_req)
                return cleaned_df
            else:
                print("No cleaned_df data found in the response.")
        else:
            print("Request to /clean/v2 failed with status code:", response.status_code)
            print("Response content:", response.content)


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
