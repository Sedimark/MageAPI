import pandas as pd
import requests
from default_repo.sedimark_demo import secret
from default_repo.sedimark_demo import connector
# from mage_a
# from dqp.core import DataSource
from collections import namedtuple


if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@data_loader
def load_data_broker(*args, **kwargs):
    """
    Load data from stellio broker.

    Returns:
        found dataframe
    """

    entity_id=kwargs.get('entity_id')

    if entity_id is None:
        entity_id="urn:ngsi-ld:WeatherInformation:Forecasted:Hourly:France:Les_Orres"
        
    bucket = {'host': 'https://stellio-dev.eglobalmark.com',
          'url_keycloak': 'https://sso.eglobalmark.com/auth/realms/sedimark/protocol/openid-connect/token',
          'client_id': secret.client_id,
          'client_secret': secret.client_secret,
          'username': secret.username,
          'password': secret.password,
          'entity_id': entity_id,
          'link_context': 'https://easy-global-market.github.io/ngsild-api-data-models/projects/jsonld-contexts/sedimark.jsonld',
          'time_query': 'timerel=after&timeAt=2023-08-01T00:00:00Z'
          }

    stellio_dev = connector.DataStore_NGSILD(bucket['host'], bucket['url_keycloak'])
    stellio_dev.getToken(bucket['client_id'], bucket['client_secret'], bucket['username'], bucket['password'])

    load_data = connector.LoadData_NGSILD(data_store=stellio_dev, entity_id=bucket['entity_id'],
     context=bucket['link_context'], 
    tenant="urn:ngsi-ld:tenant:sedimark")
    load_data.run(bucket)
    df=bucket['temporal_data']
    df.reset_index(inplace=True)

    return df