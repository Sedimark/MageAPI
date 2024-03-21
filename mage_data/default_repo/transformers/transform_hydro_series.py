import pandas as pd

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@transformer
def transform(merged_df, *args, **kwargs):
    """
    Template code for a transformer block.

    Add more parameters to this function if this block has multiple parent blocks.
    There should be one parameter for each output variable from each parent block.

    Args:
        data: The output from the upstream parent block
        args: The output from any additional upstream blocks (if applicable)

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """

    merged_df['observedAt'] = pd.to_datetime(merged_df['observedAt'], errors='coerce')


    merged_df['observedAt'] = merged_df['observedAt'].dt.strftime('%Y-%m-%d %H:%M:%S')

    # selected_stations = ['X031001001','X045401001', 'X050551301']

    selected_stations = ['X031001001','X045401001','X051591001','X050551301']


    # selected_stations = ['X051591001', 'X031001001','X045401001', 'X050551301']
    # df_selected = merged_df[merged_df['waterStation'].isin(selected_stations)]

    df=merged_df.copy()

    df = merged_df[merged_df['waterStation'].isin(selected_stations)]

    df_pivoted = df.pivot(index='observedAt', columns='waterStation', values='waterFlow')

    # df_pivoted.reset_index(inplace=True)

#  ?????????????????????????????????????????????????????? reset index??????????????????

    # df_pivoted.reset_index(drop=True, inplace=True)

    print(f"is null X045401001 {df_pivoted['X045401001'].isna().sum()}")
    # print(f"is null X051591001 {df_pivoted['X051591001'].isna().sum()}")
    print(f"is null X031001001 {df_pivoted['X031001001'].isna().sum()}")
    print(f"target: is null X050551301 {df_pivoted['X050551301'].isna().sum()}")
    # print(f"is null X061000201 {df_pivoted['X061000201'].isna().sum()}")
    # print(f"is null X043401001 {df_pivoted['X043401001'].isna().sum()}")
    print(f"is null X051591001  {df_pivoted['X051591001'].isna().sum()}")
    # print(f"is null X045631001  {df_pivoted['X045631001'].isna().sum()}")


    
    return df_pivoted#.head(6)