import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


def plot_waterFlow(df):
    
    station_ids = df['waterStation'].unique()
    print(f"station ids: {station_ids}")


    station_ids = df['waterStation'].unique()


    frequencies = []
    most_appearing_values = []

    for station_id in station_ids:
        # print(f"Station ID: {station_id}")
        
        station_data = df[df['waterStation'] == station_id]
        
        description = station_data['waterFlow'].describe()
        frequency = description['freq']
        most_appearing_value = str(description['top'])
        
        frequencies.append(frequency)
        most_appearing_values.append(most_appearing_value)


    plt.figure(figsize=(10, 6))

    plt.bar(station_ids, most_appearing_values, color='skyblue')

    plt.xlabel('Station ID')
    plt.ylabel('Water Flow Level')
    plt.title('Most Appearing Value for Water Flow of Each Station')
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()


def load_csv_data(file_name):
    df=pd.read_csv(f'default_repo/data_loaders/input/{file_name}.csv', sep=";")
    
    selected_columns = df.loc[:, ['<CdStationHydro>', '<DtObsElaborHydro>','<ResObsElaborHydro>']] 
    selected_columns = selected_columns.rename(columns={'<CdStationHydro>': 'waterStation', '<DtObsElaborHydro>': 'observedAt','<ResObsElaborHydro>':'waterFlow'})  

    df = selected_columns.iloc[1:]

    df['observedAt'] = pd.to_datetime(df['observedAt'], errors='coerce')

    df['observedAt'] = df['observedAt']
    
    return df




@data_loader
def load_data(*args, **kwargs):
    """
    Template code for loading data from any source.

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """

    file_name='export_hydro_series_1960_to_1989'

    df1=load_csv_data(file_name)


    file_name='export_hydro_series_1990_to_2023'

    df2=load_csv_data(file_name)


    merged_df = pd.concat([df1, df2])



    plot_waterFlow(merged_df)


    return merged_df
    # return {}

