from typing import Dict, List
import logging
import json
import pika

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer


@transformer
def transform(messages: List[Dict], *args, **kwargs):
    # kwargs['channel'].basic_ack(messages[0].delivery_tag)
    connection = pika.BlockingConnection(
    pika.ConnectionParameters(host="localhost", port=5672))    
    # print(messages.body.decode())
    # return json.dumps({'message':messages.body.decode()})
