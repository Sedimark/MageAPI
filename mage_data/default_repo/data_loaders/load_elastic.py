from elasticsearch import Elasticsearch

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@data_loader
def load_data(data_config, *args, **kwargs):
    """
    Template code for loading data from any source.

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """
    elastic_url = data_config['default']['ELASTIC_URL']
    elastic_username = data_config['default']['ELASTIC_USERNAME']
    elastic_password = data_config['default']['ELASTIC_PASSWORD']
    es = Elasticsearch([elastic_url], timeout=1, basic_auth=(elastic_username, elastic_password), ca_certs="/home/src/sedimark/http_ca.crt", verify_certs=False)
    job_id = "water_temps_mean"
    job_config = {
        "description" : "Mean of temperature",
        "analysis_config" : {
          "bucket_span":"1h",
          "detectors": [
            {
              "detector_description": "TEMP Mean",
              "function": "mean",
              "field_name": "temperature"
            }
          ]
        },
        "data_description" : {
          "time_field":"observedAt"
        }
    }
    print(es.xpack.ml.get_jobs("water_job"))
    # es.xpack.ml.put_job(job_id=job_id, body=job_config)
    # datafeed_config = {
    #     "datafeed_id": f"datafeed-{job_id}",
    #     "job_id": job_id,
    #     "indices": ["water_data"]
    # }

    # es.xpack.ml.put_datafeed(datafeed_id=datafeed_config["datafeed_id"], body=datafeed_config)
    # es.xpack.ml.start_datafeed(datafeed_id=datafeed_config["datafeed_id"], body={"start": "now"})

    # es.xpack.ml.open_job(job_id=job_id)
    # anomalies = es.xpack.ml.get_job_stats(job_id=job_id)
    # print(anomalies)
    return {}


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'