import pandas as pd
import matplotlib.pyplot as plt

from mage_ai.io.file import FileIO
if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test



def plot_waterFlow(df):
    
   

    frequencies = []
    most_appearing_values = []

        
    description = df.describe() 
    print(description)

    frequency = description['precipitation (mm)']
    most_appearing_value = str(description['precipitation (mm)'])
        


    age_stats = df['precipitation (mm)'].describe()

    # Extract data for plotting the distribution (e.g., counts)
    plt.hist(df['precipitation (mm)'])
    plt.xlabel('Precipitation Level')
    plt.ylabel('Number of recorded values')
    plt.title('Distribution of precipitation values in the dataframe')
    plt.show()

@data_loader
def load_data_from_file(*args, **kwargs):
    """
    Loads precipitation data (snow, rain and their sum)
    """
    # filepath = 'default_repo/data_loaders/input/hourly_precipitation.csv'
    filepath = 'default_repo/data_loaders/input/le_sauze_du_lac_rain_hourly.csv' #BUN close to barage le_sauze_du_lac_rain_hourly.csv


    df=pd.read_csv(filepath)
    

    df['time'] = pd.to_datetime(df['time'])

    df.set_index('time', inplace=True)

    daily_average = df.resample('D').mean()

    daily_average = daily_average.reset_index()

    # plot_waterFlow(daily_average)

    print(len(daily_average))


    
    daily_average['observedAt'] = pd.to_datetime(daily_average['time'], errors='coerce')


    daily_average['observedAt'] = daily_average['observedAt'].dt.strftime('%Y-%m-%d %H:%M:%S')

    daily_average.index=daily_average['observedAt']

    # daily_average = daily_average.drop(['time','observedAt','rain (mm)','snowfall (cm)'], axis=1)
    daily_average = daily_average.drop(['time','observedAt'], axis=1)




    return daily_average

@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'