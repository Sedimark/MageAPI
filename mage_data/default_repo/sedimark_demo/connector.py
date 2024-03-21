import requests
import json
import numpy as np
import pandas as pd
from functools import reduce
from deepdiff import DeepDiff
from .data_model import DataStore
from .processing_model import ProcessingStep


class DataStore_NGSILD(DataStore):
    """A DataStore in a NGSI-LD broker"""
    def __init__(self, host, url_keycloak):
        self.host = host
        self.url_keycloak = url_keycloak

    def getToken(self, client_id, client_secret, username=None, password=None):
        """Retrieve a token from keycloak, to able to interact with the context broker"""
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'
            }
        if (username is None) or (password is None):
            data = {
                'client_id': client_id,
                'client_secret': client_secret,
                'grant_type': 'client_credentials'
                }
        else:
            data = {
                'client_id': client_id,
                'client_secret': client_secret,
                'username': username,
                'password': password,
                'grant_type': 'password'
                }
        r = requests.post(self.url_keycloak, data=data, headers=headers)
        if r.status_code != 200:
            raise Exception(r.json())
        self.token = r.json()['access_token']


class LoadData_NGSILD(ProcessingStep):
    """A processing step to save some data in the NGSI-LD Datastore"""
    def __init__(self, data_store: DataStore_NGSILD, entity_id, context, tenant=None):
        self.entity_id = entity_id
        self.context = context
        self.data_store = data_store
        if tenant is None:
            self.headers = {
                'Authorization': 'Bearer ' + data_store.token,
                'Link': f'<{context}>; rel="http://www.w3.org/ns/json-ld#context"; type="application/ld+json"'
                }
        else:
            self.headers = {
                'Authorization': 'Bearer ' + data_store.token,
                'Link': f'<{context}>; rel="http://www.w3.org/ns/json-ld#context"; type="application/ld+json"',
                'NGSILD-Tenant': tenant
                }

    def get_attrs_list(self, bucket):
        """Retrieve the entity from the context broker and save lists of the names of temporal and non-temporal attributes"""
        # Do a GET request on the NGSI-LD API to retrieve the entity
        r = requests.get(f'{self.data_store.host}/ngsi-ld/v1/entities/{self.entity_id}', headers=self.headers)
        if r.status_code != 200:
            raise Exception(r.json())
        # Putting the keys of the returned json into a list (except id and type as those are not attributes)
        attrs = [k for k in r.json().keys() if k not in ['id', 'type']]
        # For each attribute in attrs, we want to check if it is temporal (i.e., if it has an "observedAt") or not
        temporal_attrs = []
        non_temporal_attrs = []
        for key in attrs:
            # If the value is a list, it means that this attribute has multiple datasetId
            if type(r.json()[key]) == list:
                temporal = False
                # In this case we need to go through each dataset, if an observedAt is found in one of them, the attribute is considered temporal
                for dataset in r.json()[key]:
                    if 'observedAt' in dataset:
                        temporal = True
                        break
                if temporal:
                    temporal_attrs.append(key)
                else:
                    non_temporal_attrs.append(key)
            # If the value is not a list, it means that the attributes only has one datasetId
            else:
                if 'observedAt' in r.json()[key]:
                    temporal_attrs.append(key)
                else:
                    non_temporal_attrs.append(key)
        bucket['all_attrs'] = attrs
        bucket['temporal_attrs'] = temporal_attrs
        bucket['non_temporal_attrs'] = non_temporal_attrs

    def get_contextual_data(self, bucket):
        """Retrieve the entity from the context broker and save a snapshot of it (the whole json-ld object) in the bucket"""
        # Do a GET request on the NGSI-LD API to retrieve the entity
        r = requests.get(f'{self.data_store.host}/ngsi-ld/v1/entities/{self.entity_id}', headers=self.headers)
        if r.status_code != 200:
            raise Exception(r.json())
        exclude_keys = ['id', 'type']
        bucket['entity_type'] = r.json()['type']
        # The returned json-ld object is added to the bucket without type and id (which were added separately to the bucket)
        bucket['contextual_data'] = {k: r.json()[k] for k in set(list(r.json().keys())) - set(exclude_keys)}

    def get_temporal_data(self, bucket):
        """Retrieve the temporal representation of the entity from the context broker and convert it to a pandas DataFrame"""
        # Do a GET request on the temporal endpoint of the NGSI-LD API to retrieve the temporal representation of the entity for the requested period
        r = requests.get(f'{self.data_store.host}/ngsi-ld/v1/temporal/entities/{self.entity_id}?{bucket["time_query"]}&options=temporalValues', headers=self.headers)
        if r.status_code != 200:
            raise Exception(r.json())
        df_list = []
        # Go through all the temporal attributes
        for attrs in bucket['temporal_attrs']:
            # If the value is a list, it means that this attribute has multiple datasetId
            if type(r.json()[attrs]) == list:
                # In this case we need to go through each dataset, each dataset is converted to a single pandas DataFrame which is added to df_list
                for dataset in r.json()[attrs]:
                    # After merging, each dataset will have its own column named "attribute_name # datasetId"
                    df_list.append(pd.DataFrame(dataset['values'], columns= [f"{attrs} # {dataset['datasetId']}", 'observedAt']))
            # If the value is not a list, it means that the attributes only has one datasetId
            else:
                if 'datasetId' in r.json()[attrs]:
                    df_list.append(pd.DataFrame(r.json()[attrs]['values'], columns=[f"{attrs} # {r.json()[attrs]['datasetId']}", 'observedAt']))
                # In this case, just convert the attribute to a pandas DataFrame
                else:
                    df_list.append(pd.DataFrame(r.json()[attrs]['values'], columns=[attrs, 'observedAt']))
        # Use reduce to merge all the DataFrame contained in df_list into one
        df = reduce(lambda  left,right: pd.merge(left, right, on=['observedAt'], how='outer'), df_list)
        df.set_index('observedAt', inplace=True)
        df.sort_index(inplace=True)
        bucket['temporal_data'] = df

    def run(self, bucket):
        self.get_attrs_list(bucket)
        self.get_contextual_data(bucket)
        self.get_temporal_data(bucket)


class SaveData_NGSILD(ProcessingStep):
    """A processing step to save some data in the NGSI-LD Datastore"""
    def __init__(self, data_store: DataStore_NGSILD, entity_id, context, tenant=None):
        self.entity_id = entity_id
        self.context = context
        self.data_store = data_store
        if tenant is None:
            self.headers = {
                'Authorization': 'Bearer ' + data_store.token,
                'Link': f'<{context}>; rel="http://www.w3.org/ns/json-ld#context"; type="application/ld+json"'
                }
        else:
            self.headers = {
                'Authorization': 'Bearer ' + data_store.token,
                'Link': f'<{context}>; rel="http://www.w3.org/ns/json-ld#context"; type="application/ld+json"',
                'NGSILD-Tenant': tenant
                }

    def check_if_entity_exists(self, bucket):
        """Check if the entity on which we want to save the data exists, if not, creates it"""
        r = requests.get(f'{self.data_store.host}/ngsi-ld/v1/entities/{self.entity_id}', headers=self.headers)
        if r.status_code == 200:
            if 'entity_to_load_from' in bucket:
                self.new_entity = self.entity_id != bucket['entity_to_load_from']
                self.source_entity = True
            else:
                self.new_entity = True
                self.source_entity = False
        elif r.status_code == 404:
            self.new_entity = True
            if 'entity_to_load_from' in bucket:
                self.source_entity = True
            else:
                self.source_entity = False
            if 'entity_type' in bucket:
                new_entity_type = ['ProcessedData', bucket['entity_type']]
            else:
                new_entity_type = 'ProcessedData'
            payload = {'id': self.entity_id, 'type': new_entity_type}
            r = requests.post(f'{self.data_store.host}/ngsi-ld/v1/entities', json=payload, headers=self.headers)
            print(f'Creation of new entity: {self.entity_id} - status: {r.status_code}')
        else:
            raise Exception(r.json())

    def np_encode(self, n):
        if type(n) == np.int64:
            return int(n)
        if type(n) == np.float64:
            return float(n)
        else:
            return n

    def create_contextual_payload(self, bucket):
        """Compare processed_contextual_data with the original contextual_data, to create the payload to be sent to the API"""
        # Using DeepDiff to make the comparison
        diff = DeepDiff(bucket['contextual_data'], bucket['processed_contextual_data'])
        for key in bucket['processed_contextual_data'].keys():
            if type(bucket['processed_contextual_data'][key]) != list:
                bucket['processed_contextual_data'][key] = [bucket['processed_contextual_data'][key]]
        new_or_modified_attrs = []
        # DeepDiff returns a list of list, with the first layer being a list of different types of changes (e.g., new item, modified item, deleted item, ...)
        # And the second layer being a list of which attribute has change for each type
        for type_of_change in diff:
            for attrs in diff[type_of_change]:
                # The element of the lists are string with extra information that we don't need to keep, so split to keep only the attribute name
                new_or_modified_attrs.append(attrs.split('\'')[1])
        # The processing step can add some new columns the temporal DataFrame, without necessarily having to add the corresponding attribute in the contextual_data object
        # This part checks for some new attributes that have been added in the temporal DataFrame and that are not in the contextual_data object (to add them)
        for col in bucket['processed_temporal_data']:
            if ' $ ' in col:
                continue
            # If the column name does not contain ' # ', it means that the column name is simply an attribute name (no datasetId)
            elif ' # ' not in col:
                # In this case, check if this attribute is already in the contextual_data
                if col not in bucket['processed_contextual_data']:
                    # If not, create the attribute (in NGSI-LD compliant format) in the contextual data
                    ind = 0
                    value = bucket['processed_temporal_data'][col][ind]
                    while np.isnan(value) and ind < len(bucket['processed_temporal_data'][col]):
                        ind += 1
                        value = bucket['processed_temporal_data'][col][ind]
                    bucket['processed_contextual_data'].update({col: [{'type': 'Property', 'value': self.np_encode(value), 'observedAt': bucket['processed_temporal_data'].index[-1]}]})
                    # Add the attributes to the list of attribute that were modified
                    new_or_modified_attrs.append(col)
            # If the column name contains ' # ', it means that the column name is not simply an attribute name but an attribute name + datasetId (separated by '#', as defined in the load_data)
            else:
                # In this case, split the column name to get the attribute name and the datasetId, then the process is the same as above
                attrs = col.split(' # ')[0]
                datasetId = col.split(' # ')[1]
                if attrs not in bucket['processed_contextual_data']:
                    ind = 0
                    value = bucket['processed_temporal_data'][col][ind]
                    while np.isnan(value) and ind < len(bucket['processed_temporal_data'][col]):
                        ind += 1
                        value = bucket['processed_temporal_data'][col][ind]
                    bucket['processed_contextual_data'].update({attrs: [{'type': 'Property', 'value': self.np_encode(value), 'observedAt': bucket['processed_temporal_data'].index[-1], 'datasetId': datasetId}]})
                    new_or_modified_attrs.append(attrs)
        # In the payload, keep only the attributes that underwent some changes (creation or modifications)
        payload = {item[0]: item[1] for item in bucket['processed_contextual_data'].items() if self.new_entity or item[0] in new_or_modified_attrs}
        if self.new_entity and self.source_entity:
            payload.update({'sourceEntity': {'type': 'Relationship', 'object': bucket['entity_to_load_from']}})
        bucket['new_or_modified_attrs'] = new_or_modified_attrs
        bucket['contextual_payload'] = payload

    def create_temporal_payload(self, bucket):
        """Compare processed_temporal_data with the original temporal_data, to create the payload to be sent to the API"""
        payload = {}
        for col in bucket['processed_temporal_data'].columns:
            # If the column name does not contain ' # ', it means that the column name is simply an attribute name (no datasetId)
            if ' # ' not in col and ' $ ' not in col:
                attrs = col
                instances = []
                for ind in bucket['processed_temporal_data'].index:
                    value = bucket['processed_temporal_data'].loc[ind, col]
                    if not np.isnan(value):
                        instances.append({"type": "Property", "value": self.np_encode(value), "observedAt": ind})
                # Need to add all the sub-property of this attribute (from the contextual_data), to each instance
                missing_sub_property = [{item[0]: item[1]} for item in bucket['processed_contextual_data'][attrs].items() if item[0] not in ['type', 'value', 'observedAt']]
                for instance in instances:
                    for item in missing_sub_property:
                        instance.update(item)
                if attrs not in payload:
                    payload.update({attrs: instances})
                else:
                    payload[attrs] += instances
            # If the column name contains ' # ', it means that the column name is not simply an attribute name but an attribute name + datasetId (separated by '#', as defined in the load_data)
            elif ' # ' in col and ' $ ' not in col:
                # In this case, split the column name to get the attribute name and the datasetId, then the process is the same as above
                attrs = col.split(' # ')[0]
                datasetId = col.split(' # ')[1]
                for ind in bucket['processed_temporal_data'].index:
                    if type(bucket['processed_temporal_data'].loc[ind, col]) != np.float64:
                        print(bucket['processed_temporal_data'].loc[ind, col], type(bucket['processed_temporal_data'].loc[ind, col]))
                instances = []
                for ind in bucket['processed_temporal_data'].index:
                    value = bucket['processed_temporal_data'].loc[ind, col]
                    if not np.isnan(value):
                        instances.append({"type": "Property", "value": self.np_encode(value), "observedAt": ind, "datasetId": datasetId})
                missing_sub_property = []
                for dataset in bucket['processed_contextual_data'][attrs]:
                    if "datasetId" in dataset:
                        if dataset['datasetId'] == datasetId:
                            missing_sub_property = [{item[0]: item[1]} for item in dataset.items() if item[0] not in ['type', 'value', 'observedAt']]
                for instance in instances:
                    for item in missing_sub_property:
                        instance.update(item)
                if attrs not in payload:
                    payload.update({attrs: instances})
                else:
                    payload[attrs] += instances
        
        for col in bucket['processed_temporal_data'].columns:
            if ' # ' not in col and ' $ ' in col:
                attrs = col.split(' $ ')[0]
                sub_property = col.split(' $ ')[1]
                sub_instances = []
                for ind in bucket['processed_temporal_data'].index:
                    value = bucket['processed_temporal_data'].loc[ind, col]
                    if not np.isnan(value):
                        sub_instances.append([{"type": "Property", "value": self.np_encode(value)},ind])
                for sub_instance in sub_instances:
                    for instance in payload[attrs]:
                        if 'datasetId' not in instance and instance['observedAt'] == sub_instance[1]:
                            instance.update({sub_property: sub_instance[0]})
            elif ' # ' in col and ' $ ' in col:
                attrs = col.split(' # ')[0]
                datasetId = col.split(' # ')[1].split(' $ ')[0]
                sub_property = col.split(' # ')[1].split(' $ ')[1]
                sub_instances = []
                for ind in bucket['processed_temporal_data'].index:
                    value = bucket['processed_temporal_data'].loc[ind, col]
                    if not np.isnan(value):
                        sub_instances.append([{"type": "Property", "value": self.np_encode(value)},ind])
                for sub_instance in sub_instances:
                    for instance in payload[attrs]:
                        if instance['datasetId'] == datasetId  and instance['observedAt'] == sub_instance[1]:
                            instance.update({sub_property: sub_instance[0]})
        bucket['temporal_payload'] = payload

    def create_temporal_payload_list(self, bucket):
        """Split a payload into smaller ones"""
        # The temporal endpoint does not accept POST request with a payload larger than 2 MB
        # If the temporal_payload is larger than 2 MB, this function splits it into smaller payloads to be sent separately
        payload_list = [bucket['temporal_payload']]
        def split_payload(payload):
            first_half = {}
            second_half = {}
            for key in payload.keys():
                half = len(payload[key])//2
                first_half.update({key: payload[key][:half]})
                second_half.update({key: payload[key][half:]})
            return [first_half, second_half]
        while len(json.dumps(payload_list[-1])) > 2000000:
            temp = []
            for payload in payload_list:
                temp += split_payload(payload)
            payload_list = temp
        bucket['temporal_payload_list'] = payload_list

    def post_contextual_data(self, bucket):
        """Update the contextual data on the context broker"""
        # Do a POST request on the NGSI-LD API to update the entity
        r = requests.patch(f'{self.data_store.host}/ngsi-ld/v1/entities/{self.entity_id}', json=bucket['contextual_payload'], headers=self.headers)
        print(f'Contextual data update: 1/1 - status: {r.status_code}')
        if r.status_code != 204:
            print(r.json())

    def post_temporal_data(self, bucket):
        """Update the temporal data on the context broker"""
        # Do a POST request on the temporal endpoint of the NGSI-LD API to update the temporal representation of the entity
        n = len(bucket['temporal_payload_list'])
        for count, payload in enumerate(bucket['temporal_payload_list']):
            r = requests.post(f'{self.data_store.host}/ngsi-ld/v1/temporal/entities/{self.entity_id}/attrs', json=payload, headers=self.headers)
            print(f'Temporal data update: {count+1}/{n} - status: {r.status_code}')
            if r.status_code != 204:
                print(r.json())

    def run(self,bucket):
        self.check_if_entity_exists(bucket)
        self.create_contextual_payload(bucket)
        self.create_temporal_payload(bucket)
        # If the payload is not empty, update the contextual data
        if bucket['contextual_payload'] != {}:
            self.post_contextual_data(bucket)
        else:
            print('No new or modified contextual data to update')
        # If the payload is not empty, update the temporal data
        if bucket['temporal_payload'] != {}:
            self.create_temporal_payload_list(bucket)
            self.post_temporal_data(bucket)
        else:
            print('No new or modified temporal data to update')