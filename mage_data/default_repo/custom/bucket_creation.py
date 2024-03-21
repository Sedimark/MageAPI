import os
import yaml
import minio
from mage_ai.settings.repo import get_repo_path

if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@custom
def transform_custom(*args, **kwargs):
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

    if not client.bucket_exists("pipeline-name"):
        client.make_bucket("pipeline-name")



@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
