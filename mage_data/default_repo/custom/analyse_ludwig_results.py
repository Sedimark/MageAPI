import matplotlib.pyplot as plt
import logging

from mage_ai.settings.repo import get_repo_path
import os
import yaml
from minio import Minio
import io
from PIL import Image

logging.getLogger('matplotlib.font_manager').disabled=True

if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test




def save_plot(file_to_save, content, content_type):
    config_path = os.path.join(get_repo_path(), 'io_config.yaml')
    with open(config_path, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    client = Minio(
        config["default"]["MINIO_HOST"],
        access_key=config["default"]["MINIO_ACCESS_KEY"],
        secret_key=config["default"]["MINIO_SECRET_KEY"],
        secure=True
    )

    # Save the content to Minio
    client.put_object("ml-flow", file_to_save,
                      io.BytesIO(content), -1, content_type,
                      part_size=(1024**2)*5)



def plot_data(df, column_name):
    plt.figure(figsize=(12, 6))
    plt.plot(df['Time'][df['split']==2], df[f'{column_name}_recorded'][df['split']==2], label='Actual Recorded Data')
    plt.plot(df['Time'][df['split']==2], df[f'{column_name}_predicted'][df['split']==2], color='red', label='Predictions', marker='o')
    plt.xlabel('Time')
    plt.ylabel('Value')
    plt.xticks(rotation=45)
    plt.legend()

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    im = Image.open(buffer)
    im.show()

    # Save the plot to Minio
    save_plot("ludwig_result.png", buffer.getvalue(), "image/png")

    plt.show()

    plt.close()

@custom
def transform_custom(data, *args, **kwargs):
    """
    Args:
        data: The output from the upstream parent block (if applicable)
        args: The output from any additional upstream blocks

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """
    column_name=kwargs.get('column_name')
    print(f"column_name is {column_name}")

    if column_name is None:
        column_name="flow_urn:ngsi-ld:HydrometricStation:X045631001"
        print(f"column_name is {column_name}")

    plot_data(df=data,column_name=column_name)



