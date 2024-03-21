import os
import yaml
import folium
import tempfile
import numpy as np
import pandas as pd
from minio import Minio
from folium.plugins import TimestampedGeoJson
from mage_ai.settings.repo import get_repo_path


if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter


def load_config():
    config_path = os.path.join(get_repo_path(), 'io_config.yaml')
    with open(config_path, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

        return config
    
    return None


@data_exporter
def export_data(data, *args, **kwargs):
    """
    Exports data to some source.

    Args:
        data: The output from the upstream parent block
        args: The output from any additional upstream blocks (if applicable)

    Output (optional):
        Optionally return any object and it'll be logged and
        displayed when inspecting the block run.
    """
    coordinates = data[1]
    m = folium.Map(location=coordinates[::-1], zoom_start=10)
    features = []
    for i, row in data[0].iterrows():
        feature = {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': coordinates,
            },
            'properties': {
                'time': row['date'].strftime('%Y-%m-%d'),
                'popup': f"Date: {row['date']}<br>Value: {row['predictions'][0]}",
                'style': {'color': ''},
                'icon': 'marker',
                'iconstyle':{
                    'iconUrl': "https://minio1.sedimark.work/images/wind.png",  # URL of the custom icon representing a flow or a wave
                    'iconSize': [30, 30],  # Size of the icon
                    'iconAnchor': [15, 15],  # Anchor point of the icon
                    'popupAnchor': [0, -15]  # Popup anchor
                }
            }
        }
        features.append(feature)
    
    ts_geojson = TimestampedGeoJson(
        {'type': 'FeatureCollection', 'features': features},
        period='P1D', 
        add_last_point=True,
        auto_play=True,
        loop=True,
        max_speed=1,
        loop_button=True,
        date_options='YYYY/MM/DD',
    )

    ts_geojson.add_to(m)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = os.path.join(temp_dir, "map.html")

        m.save(file_path)

        config = load_config()
        client = Minio(
            config["default"]["MINIO_HOST"],
            access_key=config["default"]["MINIO_ACCESS_KEY"],
            secret_key=config["default"]["MINIO_SECRET_KEY"],
        )

        if not client.bucket_exists("lgboost_model"):
            client.make_bucket("lgboost_model")
        
        client.fput_object("prediction", "map.html", file_path)

