import folium
from IPython.display import display
import pandas as pd
import requests
from sedimark.sedimark_demo import secret
from sedimark.sedimark_demo import connector
from mage_ai.settings.repo import get_repo_path
import os
import yaml
from minio import Minio
import io

if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test



def save_file(file_to_save, map_object):
    config_path = os.path.join(get_repo_path(), 'io_config.yaml')
    with open(config_path, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    client = Minio(
        config["default"]["MINIO_HOST"],
        access_key=config["default"]["MINIO_ACCESS_KEY"],
        secret_key=config["default"]["MINIO_SECRET_KEY"],
        secure=True
    )

    # Convert the Folium Map to HTML
    map_html = map_object.get_root().render()

    # Save the HTML file to Minio
    client.put_object("ml-flow", file_to_save,
                      io.BytesIO(map_html.encode('utf-8')), -1, "text/html",
                      part_size=(1024**2)*5)



@custom
def transform_custom(data, *args, **kwargs):
    """
    Args:
        data: The output from the upstream parent block (if applicable)
        args: The output from any additional upstream blocks

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """


    df=data[0]
    df_coordinates=data[1]
    m = folium.Map(location=[df_coordinates['latitude'].iloc[0], df_coordinates['longitude'].iloc[0]], zoom_start=10)


    print(df_coordinates.latitude)

    for item in df_coordinates.values:
        print(item)
        folium.Marker(
                location=[item[0], item[1]],
                popup=f"<b>Station: {item[2]}</b><br>Latitude: {item[0]}</br><br>Longitude: {item[1]}</br>",
                zoom_on_click=True).add_to(m)

    display(m)
    save_file("view_stations.html", m)
