from sedimark.sedimark_demo import secret
from sedimark.sedimark_demo import connector
import copy
import numpy as np
import pandas as pd
if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter


def export_to_broker(entity_to_load_from, entity_to_save_in,data):
    bucket = {'host': 'https://stellio-dev.eglobalmark.com',
              'url_keycloak': 'https://sso.eglobalmark.com/auth/realms/sedimark/protocol/openid-connect/token',
              'client_id': secret.client_id,
              'client_secret': secret.client_secret,
              'username': secret.username,
              'password': secret.password,
              'entity_to_load_from': entity_to_load_from,
              'entity_to_save_in': entity_to_save_in,
              'link_context': 'https://raw.githubusercontent.com/easy-global-market/ngsild-api-data-models/master/sedimark/jsonld-contexts/sedimark.jsonld',
              'tenant': 'urn:ngsi-ld:tenant:sedimark',
              'time_query': 'timerel=after&timeAt=2023-08-01T00:00:00Z',
              'content_type': 'application/json'
              }

    stellio_dev = connector.DataStore_NGSILD(bucket['host'], bucket['url_keycloak'])
    stellio_dev.getToken(bucket['client_id'], bucket['client_secret'], bucket['username'], bucket['password'])


    load_data = connector.LoadData_NGSILD(data_store=stellio_dev, entity_id=bucket['entity_to_load_from'],
                                          context=bucket['link_context'], tenant="urn:ngsi-ld:tenant:sedimark")
    load_data.run(bucket)

    bucket['processed_contextual_data'] = copy.deepcopy(bucket['contextual_data'])
    bucket['processed_temporal_data'] = data.copy()

    print(f"temporal data is\n: {bucket['temporal_data']}")
    print(f"processed temporal data is\n: {bucket['processed_temporal_data']}")

    save_data = connector.SaveData_NGSILD(data_store=stellio_dev, entity_id=bucket['entity_to_save_in'],
                                          context=bucket['link_context'], tenant=bucket['tenant'])
    save_data.run(bucket)





@data_exporter
def export_data(data, *args, **kwargs):
    """
    Exports data to some source.

    Args:
        data: The output from the upstream parent block
        args: The output from any additional upstream blocks (if applicable)

    Output (optional):
        Optionally return any object and it'll be logged and
        displayed when inspecting the block run.
    """
    column_name=kwargs.get('column_name')
    print(f"column_name is -from args {column_name}")

    if column_name is None:
        column_name="flow_urn:ngsi-ld:HydrometricStation:X045631001"
        print(f"column_name is {column_name}")




    data.rename(columns=lambda x: x.replace('_', ' # '), inplace=True)
    
    data=data.rename(columns={'Time': 'observedAt'})

    data.index=data['observedAt']

    data.drop(columns=['split','observedAt'], inplace=True)

    print(data.columns)
    print(f"data to send to broker is: \n{data.head().to_string()}")



    entity_to_load_from = column_name.split('_')[-1]

    print(f"entity_to_load_from: {entity_to_load_from}")

    entity_to_save_in=f"{entity_to_load_from}:processed"
    print(f"entity_to_save_in: {entity_to_save_in}")

    export_to_broker(entity_to_load_from, entity_to_save_in,data)

