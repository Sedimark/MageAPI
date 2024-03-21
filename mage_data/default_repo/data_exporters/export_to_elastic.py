from elasticsearch import Elasticsearch
from uuid import uuid4

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter


@data_exporter
def export_data(data_broker, data_config, *args, **kwargs):
    """
    Exports data to some source.

    Args:
        data: The output from the upstream parent block
        args: The output from any additional upstream blocks (if applicable)

    Output (optional):
        Optionally return any object and it'll be logged and
        displayed when inspecting the block run.
    """
    elastic_url = data_config['default']['ELASTIC_URL']
    elastic_username = data_config['default']['ELASTIC_USERNAME']
    elastic_password = data_config['default']['ELASTIC_PASSWORD']
    es = Elasticsearch([elastic_url], timeout=1, basic_auth=(elastic_username, elastic_password), ca_certs="/home/src/sedimark/http_ca.crt", verify_certs=False)
    
    index_name = "water_data" if kwargs.get("index_name") is None else kwargs.get("index_name")

    for _, row in data_broker.iterrows():
        doc = row.to_dict()
        es.index(index=index_name, id=str(uuid4()), document=doc)
