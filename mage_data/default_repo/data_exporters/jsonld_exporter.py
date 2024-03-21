import json
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
    # Specify your data exporting logic here
    jsonld_filepath='demo/data_exporters/output/bike_lane.jsonld'
    # Save the NGSI-LD data to a JSON-LD file
    with open(jsonld_filepath, 'w') as output_file:
        json.dump(data, output_file, indent=4)


