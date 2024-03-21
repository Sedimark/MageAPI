import pandas as pd
import requests
from default_repo.sedimark_demo import secret
from default_repo.sedimark_demo import connector

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test
    



# entity_id="urn:ngsi-ld:HydrometricStation:X045631001"
# entity_id="urn:ngsi-ld:HydrometricStation:X041541001"
# entity_id="urn:ngsi-ld:HydrometricStation:X043401001"
# entity_id"urn:ngsi-ld:HydrometricStation:X045401001"
# entity_id"urn:ngsi-ld:HydrometricStation:X031001001"
# entity_id="urn:ngsi-ld:HydrometricStation:X051591001"
# entity_id="urn:ngsi-ld:HydrometricStation:X061000201"


def query_broker(entity_id):
    bucket = {'host': 'https://stellio-dev.eglobalmark.com',
          'url_keycloak': 'https://sso.eglobalmark.com/auth/realms/sedimark/protocol/openid-connect/token',
          'client_id': secret.client_id,
          'client_secret': secret.client_secret,
          'username': secret.username,
          'password': secret.password,
          'entity_id':entity_id,
          "link_context":'https://easy-global-market.github.io/ngsild-api-data-models/projects/jsonld-contexts/sedimark.jsonld',
          
          'time_query': 'timerel=after&timeAt=2023-08-01T00:00:00Z'
          }

    stellio_dev = connector.DataStore_NGSILD(bucket['host'], bucket['url_keycloak'])
    stellio_dev.getToken(bucket['client_id'], bucket['client_secret'], bucket['username'], bucket['password'])

    load_data = connector.LoadData_NGSILD(data_store=stellio_dev, entity_id=bucket['entity_id'], context=bucket['link_context'], tenant="urn:ngsi-ld:tenant:sedimark")
    load_data.run(bucket)

    df=bucket['temporal_data']

    df_coordinates=bucket['contextual_data']['location']['value']['coordinates']
    print(df_coordinates)
    

    df.rename(columns={'flow': f'flow_{entity_id}'}, inplace=True)
    
    df.rename(columns={'waterLevel': f'waterLevel_{entity_id}'}, inplace=True)


    return df,df_coordinates


def get_temperature_data():
    entity_id="urn:ngsi-ld:WeatherInformation:Forecasted:Hourly:France:Les_Orres"
  
    bucket = {'host': 'https://stellio-dev.eglobalmark.com',
          'url_keycloak': 'https://sso.eglobalmark.com/auth/realms/sedimark/protocol/openid-connect/token',
          'client_id': secret.client_id,
          'client_secret': secret.client_secret,
          'username': secret.username,
          'password': secret.password,
          'entity_id': entity_id,
          "link_context":'https://easy-global-market.github.io/ngsild-api-data-models/projects/jsonld-contexts/sedimark.jsonld',
          'time_query': 'timerel=after&timeAt=2023-08-01T00:00:00Z'
          }

    stellio_dev = connector.DataStore_NGSILD(bucket['host'], bucket['url_keycloak'])
    stellio_dev.getToken(bucket['client_id'], bucket['client_secret'], bucket['username'], bucket['password'])

    load_data = connector.LoadData_NGSILD(data_store=stellio_dev, entity_id=bucket['entity_id'],
     context=bucket['link_context'], 
    tenant="urn:ngsi-ld:tenant:sedimark")
    load_data.run(bucket)
    df=bucket['temporal_data']

    # get all temperature columns from dataframe
    temperature_columns = [col for col in df.columns if 'temperature' in col.lower()]

    df=df[temperature_columns]


    df.reset_index(inplace=True)

    return df



@data_loader
def load_data(*args, **kwargs):
    """
    Template code for loading data from any source.

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """


    water_df = pd.DataFrame()
    df_coordinates_all=pd.DataFrame(columns=['latitude','longitude','station_id'])

    
    entity_id=kwargs.get('entity_id')
    print(f"entity_id is {entity_id}")

    if entity_id is None:
        entity_id="urn:ngsi-ld:HydrometricStation:X031001001"

        print(f"entity_id is {entity_id}")




    df,df_coordinates=query_broker(entity_id)

    water_df = df


    water_df = water_df.sort_values(by='observedAt')
    water_df['observedAt']=water_df.index


    # Reset the index of the resulting DataFrame
    water_df = water_df.reset_index(drop=True)

    print(water_df.tail())

    temperature_df = get_temperature_data()
    water_df = water_df.merge(temperature_df, on="observedAt", how="outer")

    return [water_df, df_coordinates]


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'