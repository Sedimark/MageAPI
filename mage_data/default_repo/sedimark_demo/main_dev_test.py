import connector
import secret
import copy

bucket = {'host': 'https://stellio-dev.eglobalmark.com',
          'url_keycloak': 'https://sso.eglobalmark.com/auth/realms/stellio-dev/protocol/openid-connect/token',
          'client_id': secret.client_id,
          'client_secret': secret.client_secret,
          'entity_id': 'urn:ngsi-ld:WeatherObserved:EGM-Farm-Demo',
          'link_context': 'https://raw.githubusercontent.com/easy-global-market/ngsild-api-data-models/ec6bcc2ce73f29a8398188b75136c5a7f720cd6a/precipitation/jsonld-contexts/precipitationCompouned.jsonld',
          'time_query': 'timerel=after&timeAt=2023-09-15T00:00:00Z'}

stellio_dev = connector.DataStore_NGSILD(bucket['host'], bucket['url_keycloak'])
stellio_dev.getToken(bucket['client_id'], bucket['client_secret'])

print('\nTest changes\n')

load_data = connector.LoadData_NGSILD(stellio_dev, bucket['entity_id'], bucket['link_context'])
load_data.run(bucket)

bucket['processed_contextual_data'] = copy.deepcopy(bucket['contextual_data'])
bucket['processed_contextual_data']['name']['value'] = 'EGM-Farm-Demo-test'
bucket['processed_contextual_data']['precipitation']['period']['value'] = 5

bucket['processed_temporal_data'] = bucket['temporal_data'].copy()
bucket['processed_temporal_data']['humidity'] = bucket['processed_temporal_data']['humidity'] + 10

save_data = connector.SaveData_NGSILD(stellio_dev, bucket['entity_id'], bucket['link_context'])
save_data.run(bucket)

print('\nRevert test changes\n')

load_data = connector.LoadData_NGSILD(stellio_dev, bucket['entity_id'], bucket['link_context'])
load_data.run(bucket)

bucket['processed_contextual_data'] = copy.deepcopy(bucket['contextual_data'])
bucket['processed_contextual_data']['name']['value'] = 'EGM-Farm-Demo'
bucket['processed_contextual_data']['precipitation']['period']['value'] = 10

bucket['processed_temporal_data'] = bucket['temporal_data'].copy()
bucket['processed_temporal_data']['humidity'] = bucket['processed_temporal_data']['humidity'] - 10

save_data = connector.SaveData_NGSILD(stellio_dev, bucket['entity_id'], bucket['link_context'])
save_data.run(bucket)

print('\nNo changes\n')

load_data = connector.LoadData_NGSILD(stellio_dev, bucket['entity_id'], bucket['link_context'])
load_data.run(bucket)

bucket['processed_contextual_data'] = copy.deepcopy(bucket['contextual_data'])
bucket['processed_temporal_data'] = bucket['temporal_data'].copy()

save_data = connector.SaveData_NGSILD(stellio_dev, bucket['entity_id'], bucket['link_context'])
save_data.run(bucket)
