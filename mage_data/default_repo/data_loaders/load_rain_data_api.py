import openmeteo_requests

import requests_cache
import pandas as pd
from retry_requests import retry


if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

def get_rain_data():

    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    # make request to weather APIMake sure all required weather variables are listed here
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": 44.4833,
        "longitude": 6.3167,
        "start_date": "2024-03-01",
        "end_date": "2024-03-18",
        "hourly": "rain"
    }
    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]
    print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
    print(f"Elevation {response.Elevation()} m asl")

    # Process hourly data for Le Sauze Du Lac
    hourly = response.Hourly()
    hourly_rain = hourly.Variables(0).ValuesAsNumpy()

    hourly_data = {"time": pd.date_range(
        start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
        end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = hourly.Interval()),
        inclusive = "left"
    )}
    hourly_data["rain"] = hourly_rain

    df = pd.DataFrame(data = hourly_data)


    # create average values by day
    
    df['time'] = pd.to_datetime(df['time'])

    df.set_index('time', inplace=True)

    daily_average = df.resample('D').mean()

    daily_average = daily_average.reset_index()


    
    daily_average['observedAt'] = pd.to_datetime(daily_average['time'], errors='coerce')


    daily_average['observedAt'] = daily_average['observedAt'].dt.strftime('%Y-%m-%d %H:%M:%S')

    daily_average.index=daily_average['observedAt']

    daily_average = daily_average.drop(['time','observedAt'], axis=1)


    return daily_average


@data_loader
def load_data_from_api(*args, **kwargs):
    """
    Template for loading data from API
    """
    hourly_dataframe=get_rain_data()

    return hourly_dataframe


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'