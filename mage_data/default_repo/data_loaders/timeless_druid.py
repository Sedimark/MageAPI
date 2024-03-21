import pika
if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', port=5673))

def callback(ch, method, properties, body):
    print(f" [x] Received {body}")

@data_loader
def load_data(*args, **kwargs):
    """
    Template code for loading data from any source.

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """
    channel = connection.channel()
    channel.queue_declare(queue='default')
    channel.basic_consume(queue='default',
                      auto_ack=True,
                      on_message_callback=callback)

    channel.start_consuming()

    return {}


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'