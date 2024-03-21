import pandas as pd
import requests
from sedimark.sedimark_demo import secret
from sedimark.sedimark_demo import connector

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
    entity_id=kwargs.get('entity_id')
    print(f"entity id is {entity_id}")

    if entity_id is None:
        entity_id="urn:ngsi-ld:WeatherInformation:Forecasted:Hourly:France:Les_Orres"
        print(f"entity id is {entity_id}")

    bucket = {'host': 'https://stellio-dev.eglobalmark.com',
          'url_keycloak': 'https://sso.eglobalmark.com/auth/realms/sedimark/protocol/openid-connect/token',
          'client_id': secret.client_id,
          'client_secret': secret.client_secret,
          'username': secret.username,
          'password': secret.password,
          'entity_id':entity_id,

        #   'entity_id': 'urn:ngsi-ld:WeatherInformation:Forecasted:Hourly:France:Les_Orres',
          'link_context': 'https://raw.githubusercontent.com/easy-global-market/ngsild-api-data-models/master/sedimark/jsonld-contexts/sedimark.jsonld',
          'time_query': 'timerel=after&timeAt=2023-08-01T00:00:00Z'
          }

    stellio_dev = connector.DataStore_NGSILD(bucket['host'], bucket['url_keycloak'])
    stellio_dev.getToken(bucket['client_id'], bucket['client_secret'], bucket['username'], bucket['password'])

    load_data = connector.LoadData_NGSILD(data_store=stellio_dev, entity_id=bucket['entity_id'], context=bucket['link_context'], tenant="urn:ngsi-ld:tenant:sedimark")
    load_data.run(bucket)
    df=bucket['temporal_data']


    df.reset_index(inplace=True)

    return df


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'