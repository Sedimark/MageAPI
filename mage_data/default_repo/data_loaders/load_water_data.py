import pandas as pd
import requests
from default_repo.sedimark_demo import secret
from default_repo.sedimark_demo import connector

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test
    

entity_ids=[
"urn:ngsi-ld:HydrometricStation:X031001001",
"urn:ngsi-ld:HydrometricStation:X050551301", #missing data
"urn:ngsi-ld:HydrometricStation:X051591001"
]


def query_broker(entity_id):
    bucket = {'host': 'https://stellio-dev.eglobalmark.com',
          'url_keycloak': 'https://sso.eglobalmark.com/auth/realms/sedimark/protocol/openid-connect/token',
          'client_id': secret.client_id,
          'client_secret': secret.client_secret,
          'username': secret.username,
          'password': secret.password,
          'entity_id':entity_id,
          "link_context":'https://easy-global-market.github.io/ngsild-api-data-models/projects/jsonld-contexts/sedimark.jsonld',
          'time_query': 'timerel=after&timeAt=2024-03-01T00:00:00Z'
          }

    stellio_dev = connector.DataStore_NGSILD(bucket['host'], bucket['url_keycloak'])
    stellio_dev.getToken(bucket['client_id'], bucket['client_secret'], bucket['username'], bucket['password'])

    load_data = connector.LoadData_NGSILD(data_store=stellio_dev, entity_id=bucket['entity_id'], context=bucket['link_context'], tenant="urn:ngsi-ld:tenant:sedimark")
    
    
    df = pd.DataFrame()  

    load_data.run(bucket)

    df=bucket['temporal_data']        

    df.rename(columns={'flow': f'flow_{entity_id}'}, inplace=True)
        
    df.rename(columns={'waterLevel': f'waterLevel_{entity_id}'}, inplace=True)

    return df




@data_loader
def load_data(*args, **kwargs):
    """
    Template code for loading data from the broker
    """


    water_df = pd.DataFrame()


    for entity_id in entity_ids:
        try:
            df=query_broker(entity_id)
        except TypeError:
            continue

        if water_df.empty:
            water_df = df
        else:
            if 'observedAt' not in df.columns:
                print(f"'observedAt' column not found in DataFrame for entity_id {entity_id}. Skipping...")
            else:
                water_df = water_df.merge(df.reset_index(), on='observedAt', how='outer')

    return water_df


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'