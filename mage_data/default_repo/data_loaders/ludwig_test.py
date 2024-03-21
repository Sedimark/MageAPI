import pandas as pd
from ludwig.utils.data_utils import add_sequence_feature_column
import logging
from ludwig.api import LudwigModel

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

csv_filepath='sedimark/data_loaders/input/df_result.csv'


@data_loader
def load_data(*args, **kwargs):
    """
    Template code for loading data from any source.

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """
    # Specify your data loading logic here

    df=pd.read_csv(csv_filepath, index_col=[0])
    column_name='flow_urn:ngsi-ld:HydrometricStation:X045631001'

    df_new = pd.DataFrame({
            "Time": df["observedAt"],
            column_name: df[column_name]
    })


    # 10% test size
    train_size = int(0.7 * len(df_new))
    vali_size = int(0.2 * len(df_new))

    # train, validation, test split
    df_new['split'] = 0
    df_new.loc[
        (
            (df_new.index.values >= train_size) &
            (df_new.index.values < train_size + vali_size)
        ),
        ('split')
    ] = 1
    df_new.loc[
        df_new.index.values >= train_size + vali_size,
        ('split')
    ] = 2



    # prepare timeseries input feature colum
    # (here we are using 20 preceding values to predict the target)
    add_sequence_feature_column(df_new, column_name, 20)

    config = {
    "input_features": [
        {
        "name": "flow_urn:ngsi-ld:HydrometricStation:X045631001_feature",    # The name of the input column
        "type": "timeseries",     # Data type of the input column
        "encoder": {"type": "rnn", "embedding_size": 32,"state_size":32}
        },

    ],
    "output_features": [
        {
        "name": "flow_urn:ngsi-ld:HydrometricStation:X045631001",
        "type": "number",
        }
    ],
    "trainer": {
        "epochs": 10,
        "learning_rate": 0.0002,
        # "optimizer": {"type": "adamw"},
        # "use_mixed_precision": True,
        # "learning_rate_scheduler": {"decay": "linear", "warmup_fraction": 0.2},
        # "batch_size": 32
    }
    }


    model = LudwigModel(config, logging_level=logging.INFO)


    train_stats, preprocessed_data, output_directory = model.train(dataset=df_new,random_seed=42)

    # predictions, _ = model.predict(dataset=df_new)

    # return predictions



@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'