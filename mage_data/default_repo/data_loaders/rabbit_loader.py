import pika
from mage_ai.data_preparation.decorators import data_loader
from mage_ai.data_preparation.decorators import test


connection = pika.BlockingConnection(
    pika.ConnectionParameters(host="localhost", port=5672))


def callback(ch, method, properties, body):
    print(" [x] Received: {}".format(body))

@data_loader
def load_data_from_file(*args, **kwargs):
    """
    Template for loading data from filesystem.
    Load data from 1 file or multiple file directories.

    For multiple directories, use the following:
        FileIO().load(file_directories=['dir_1', 'dir_2'])

    Docs: https://docs.mage.ai/design/data-loading#fileio
    """
    # filepath = 'path/to/your/file.csv'

        
    # Connect to RabbitMQ server
    # connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # Declare a queue to consume messages from
    queue_name = 'test_queue_rabbit'
    channel.queue_declare(queue='test_queue_rabbit', durable=True)

    # Set up the consumer to use the callback function
    channel.basic_consume(queue=queue_name,
                        on_message_callback=callback,
                        auto_ack=True)

    print(' [*] Waiting for messages. To exit, press CTRL+C')
    channel.start_consuming()

    # return FileIO().load(filepath)


# 

@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
