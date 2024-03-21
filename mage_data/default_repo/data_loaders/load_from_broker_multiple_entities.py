import pandas as pd
import requests
from sedimark.sedimark_demo import secret
from sedimark.sedimark_demo import connector

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test
    
# "urn:ngsi-ld:HydrometricStation:X050551301",


entity_ids=[
"urn:ngsi-ld:HydrometricStation:X031001001",
"urn:ngsi-ld:HydrometricStation:X041541001",
"urn:ngsi-ld:HydrometricStation:X043401001",
"urn:ngsi-ld:HydrometricStation:X045401001",
"urn:ngsi-ld:HydrometricStation:X045631001",
"urn:ngsi-ld:HydrometricStation:X051591001",
"urn:ngsi-ld:HydrometricStation:X061000201",
"urn:ngsi-ld:HydrometricStation:X050551301" 
]


def query_broker(entity_id):
    bucket = {'host': 'https://stellio-dev.eglobalmark.com',
          'url_keycloak': 'https://sso.eglobalmark.com/auth/realms/sedimark/protocol/openid-connect/token',
          'client_id': secret.client_id,
          'client_secret': secret.client_secret,
          'username': secret.username,
          'password': secret.password,
          'entity_id':entity_id,
          "link_context":'https://easy-global-market.github.io/ngsild-api-data-models/sedimark/jsonld-contexts/sedimark.jsonld',
          'time_query': 'timerel=after&timeAt=2023-08-01T00:00:00Z'
          }

    stellio_dev = connector.DataStore_NGSILD(bucket['host'], bucket['url_keycloak'])
    stellio_dev.getToken(bucket['client_id'], bucket['client_secret'], bucket['username'], bucket['password'])

    load_data = connector.LoadData_NGSILD(data_store=stellio_dev, entity_id=bucket['entity_id'], context=bucket['link_context'], tenant="urn:ngsi-ld:tenant:sedimark")
    
    
    df = pd.DataFrame()  

    try:
        load_data.run(bucket)

        df=bucket['temporal_data']

        df_coordinates=bucket['contextual_data']['location']['value']['coordinates']
        

        df.rename(columns={'flow': f'flow_{entity_id}'}, inplace=True)
        
        df.rename(columns={'waterLevel': f'waterLevel_{entity_id}'}, inplace=True)
    except TypeError:
        df_coordinates=bucket['contextual_data']['location']['value']['coordinates']



    return df,df_coordinates




@data_loader
def load_data(*args, **kwargs):
    """
    Template code for loading data from any source.

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """


    water_df = pd.DataFrame()
    df_coordinates_all=pd.DataFrame(columns=['latitude','longitude','station_id'])


    # Create empty lists to store latitude and longitude values
    latitude_list = []
    longitude_list = []
    stations=[]


    for entity_id in entity_ids:
        df,df_coordinates=query_broker(entity_id)
        print(f"df_coordinates[1] {df_coordinates[1]}; len df {len(df)}")

        # if df.empty:
        #     print(f"DataFrame for entity_id {entity_id} is empty. Skipping...")
        #     continue



        if water_df.empty:
            water_df = df
        else:
            if 'observedAt' not in df.columns:
                print(f"'observedAt' column not found in DataFrame for entity_id {entity_id}. Skipping...")
                # continue
            # water_df = water_df.merge(df.reset_index(), on='observedAt', how='inner')
            else:
                water_df = water_df.merge(df.reset_index(), on='observedAt', how='outer')

        # Append latitude and longitude values to the lists
        latitude_list.append(df_coordinates[1])
        longitude_list.append(df_coordinates[0])
        stations.append(entity_id)

    # Assign the entire lists to the DataFrame columns
    df_coordinates_all['latitude'] = latitude_list
    df_coordinates_all['longitude'] = longitude_list
    df_coordinates_all['station_id'] = stations

    water_df = water_df.sort_values(by='observedAt')


    # Reset the index of the resulting DataFrame
    water_df = water_df.reset_index(drop=True)

    print(f"df_coordinates_all {df_coordinates_all}")



    return [water_df,df_coordinates_all]


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'