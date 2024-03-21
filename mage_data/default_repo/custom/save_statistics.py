import os
import io
import yaml
import json
import pandas as pd
from minio import Minio
from mage_ai.settings.repo import get_repo_path

if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@custom
def transform_custom(df, *args, **kwargs):
    """
    Args:
        data: The output from the upstream parent block (if applicable)
        args: The output from any additional upstream blocks

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """
    config_path = os.path.join(get_repo_path(), 'io_config.yaml')
    with open(config_path, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    client = Minio(
        config["default"]["MINIO_HOST"],
        access_key=config["default"]["MINIO_ACCESS_KEY"],
        secret_key=config["default"]["MINIO_SECRET_KEY"],
        secure=True
    )

    client.put_object("sedimark-outlier-removal", "head.json",
                  io.BytesIO(df.head().to_json().encode('utf-8')), -1, "application/json",
                  part_size=(1024**2)*5)

    data = []

    for column in df.columns:
        if pd.api.types.is_numeric_dtype(df[column]):
            dct = {
                "type": "hist",
                "hist": {},
                "column_name": column
            }

            unique_values = df[column].unique()

            for unique_value in unique_values:
                for k, v in df[column].loc[df[column] == unique_value].to_dict().items():
                    dct["hist"][k] = v

            data.append(dct)
        else:
            if len(df[column].unique()) <= 5:
                dct = {
                    "type": "percentage",
                    "percentage_body": {},
                    "column_name": column
                }
                unique_values = df[column].unique()
                for unique_value in unique_values:
                    dct["percentage_body"][unique_value] = round(len(df[column].loc[df[column] == unique_value]) /
                                                                 len(df[column]) * 100, 2)

                data.append(dct)
            else:
                dct = {
                    "type": "unique_values",
                    "unique_values": len(df[column].unique()),
                    "column_name": column
                }

                data.append(dct)

    client.put_object("sedimark-outlier-removal", "statistics.json",
              io.BytesIO(json.dumps(data, indent=4).encode('utf-8')), -1, "application/json",
              part_size=(1024**2)*5)

    return df
