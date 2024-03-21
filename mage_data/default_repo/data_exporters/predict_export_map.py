import folium
from folium.plugins import TimestampedGeoJson
import pandas as pd
import numpy as np


if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter


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
    m = folium.Map(location=data[1], zoom_start=10)
    features = [
        {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': data[1],
            },
            'properties': {
                'time': row['time'],
                'style': {'color': ''},
                'icon': 'circle',
                'iconstyle':{
                    'fillColor': 'red',
                    'fillOpacity': 0.6,
                    'stroke': 'false',
                    'radius': 10
                }
            }
        } for i, row in df.iterrows()
    ]


