from mage_ai.settings.repo import get_repo_path
from os import path
import yaml
import openai

if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@custom
def transform_custom(data, *args, **kwargs):
    """
    Args:
        data: The output from the upstream parent block (if applicable)
        args: The output from any additional upstream blocks

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """

    # config openAI
    config_path = path.join(get_repo_path(), 'io_config.yaml')
    with open(config_path, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    
    OPENAI_API_TYPE = config['default']['OPENAI_API_TYPE']
    OPENAI_API_BASE = config['default']['OPENAI_API_BASE']
    OPENAI_API_KEY = config['default']['OPENAI_API_KEY']
    OPENAI_API_VERSION = config['default']['OPENAI_API_VERSION']

    openai.api_type = OPENAI_API_TYPE
    openai.api_base = OPENAI_API_BASE
    openai.api_version = OPENAI_API_VERSION
    openai.api_key=OPENAI_API_KEY
    # dict_example={"Measurement":"Temperature", "MeasurementUnit":"Celsius","Period":"DateTime"}

    start_phrase = f"""give me the most important tags to describe the given data sample in a general way: {data.head()}"""
    print(data.head())
    response = openai.Completion.create( engine="text-davinci-003", prompt=start_phrase,#, max_tokens=200)

    max_tokens=800,
    top_p=0.95,
    frequency_penalty=0,
    presence_penalty=0,
    stop=None)

    chosen_tags = response['choices'][0]['text']


    return chosen_tags


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'


# tags: 'Temperature, Date, Time, Measurement, Measurement Unit'