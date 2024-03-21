import connector
import secret
import copy

bucket = {'host': 'https://stellio-dev.eglobalmark.com',
          'url_keycloak': 'https://sso.eglobalmark.com/auth/realms/sedimark/protocol/openid-connect/token',
          'client_id': secret.client_id_sedimark,
          'client_secret': secret.client_secret_sedimark,
          'entity_id': 'urn:ngsi-ld:WeatherInformation:Forecasted:Hourly:France:Les_Orres',
          'link_context': 'https://raw.githubusercontent.com/easy-global-market/ngsild-api-data-models/master/sedimark/jsonld-contexts/sedimark.jsonld',
          'tenant': 'urn:ngsi-ld:tenant:sedimark',
          'time_query': 'timerel=after&timeAt=2020-01-01T00:00:00Z'}

stellio_dev = connector.DataStore_NGSILD(bucket['host'], bucket['url_keycloak'])
stellio_dev.getToken(bucket['client_id'], bucket['client_secret'])

load_data = connector.LoadData_NGSILD(stellio_dev, bucket['entity_id'], bucket['link_context'], bucket['tenant'])
load_data.run(bucket)

bucket['temporal_data'].to_csv('./WeatherInforamtion_Les_Orres.csv')

