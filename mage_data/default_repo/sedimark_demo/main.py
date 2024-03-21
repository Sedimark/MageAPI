import connector
import secret

bucket = {'host': 'https://stellio-dev.eglobalmark.com',
          'url_keycloak': 'https://sso.eglobalmark.com/auth/realms/sedimark/protocol/openid-connect/token',
          'client_id': secret.client_id,
          'client_secret': secret.client_secret,
          'username': secret.username,
          'password': secret.password,
          'entity_id': 'urn:ngsi-ld:WeatherInformation:Forecasted:Hourly:France:Les_Orres',
          'link_context': 'https://raw.githubusercontent.com/easy-global-market/ngsild-api-data-models/master/sedimark/jsonld-contexts/sedimark.jsonld',
          'time_query': 'timerel=after&timeAt=2023-08-01T00:00:00Z'
          }

stellio_dev = connector.DataStore_NGSILD(bucket['host'], bucket['url_keycloak'])
stellio_dev.getToken(bucket['client_id'], bucket['client_secret'], bucket['username'], bucket['password'])

load_data = connector.LoadData_NGSILD(data_store=stellio_dev, entity_id=bucket['entity_id'], context=bucket['link_context'], tenant="urn:ngsi-ld:tenant:sedimark")
load_data.run(bucket)

# print(bucket['contextual_data'])
# print(bucket['temporal_data'])

df=bucket['temporal_data']
df.to_csv("temporal_data.csv")
print(df.columns)
print(df.head().to_string())
