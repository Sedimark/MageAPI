##Copyright 2023 NUID UCD. All Rights Reserved.


import pandas as pd
import numpy as np
import os
from .core import DataFrame, DataSource
from collections import namedtuple
import datetime


_DATA_FOLDER_ROOT = "./datasets"


def read_csv(path, test_columns=[], time_column=None, numeric_columns=[]):
    df = pd.read_csv(path)

    return DataFrame(
        df,
        test_columns=test_columns,
        time_column=time_column,
        numeric_columns=numeric_columns,
    )


def load_tods_yahoo(path=None):
    if not path:
        path = os.path.join(_DATA_FOLDER_ROOT, "yahoo_sub_5.csv")
    df = read_csv(
        path,
        test_columns=["anomaly"],
        time_column="timestamp",
        numeric_columns=["value_0", "value_1", "value_2", "value_3", "value_4"],
    )
    begin = datetime.datetime.now()
    time_vals = df["timestamp"].values - df["timestamp"].min()
    new_time_vals = []
    for i in time_vals:
        new_time_vals.append(begin + datetime.timedelta(days=int(i)))
    df["timestamp"] = new_time_vals
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


def load_egm(path=None):
    if not path:
        path = os.path.join(_DATA_FOLDER_ROOT, "low_cost_weather_station/")

    os.listdir(path)
    d = {}
    for f in os.listdir(path):
        name = f.split("-")[0]
        df = pd.read_csv(f"{path}/{f}")
        d[name] = df

    time = d["Illuminance"]["Time"].values
    cols = {d[k].columns[1]: d[k][d[k].columns[1]] for k in d}
    cols["ts"] = time
    df = pd.DataFrame(cols)
    df["illuminance"] = df["illuminance"].apply(lambda x: float(x.split(" ")[0]))
    df["precipitation"] = df["precipitation"].apply(lambda x: float(x.split(" ")[0]))
    df["irradiance"] = df["irradiance"].apply(lambda x: float(x.split(" ")[0]))
    df["windspeedgust"] = df["windspeedgust"].apply(lambda x: float(x.split(" ")[0]))
    df["windspeedavg"] = df["windspeedavg"].apply(lambda x: float(x.split(" ")[0]))
    df["temperature"] = df["temperature"].apply(lambda x: float(x.split(" ")[0]))
    df["humidity"] = df["humidity"].apply(lambda x: float(x.strip("%")))
    df["ts"] = pd.to_datetime(df["ts"])
    df = df.sort_values(by="ts")

    SensorRange = namedtuple("SensorRange", "min max")

    extra_data_info = {
        "temperature": {
            "range": SensorRange(-30, 60),
            "Accuracy": 1,
            "Resolution": 0.1,
            "type": float,
        },
        "humidity": {
            "range": SensorRange(10, 99),
            "Accuracy": 5,
            "Resoultion": None,
            "type": float,
        },
        "precipitation": {
            "range": SensorRange(0, 9999),
            "Accuracy": 10,
            "Resolution": "complicated!",
            "type": float,
        },
        "windspeedavg": {
            "range": SensorRange(0, 50),
            "Accuracy": "complicated",
            "type": float,
        },
        "illuminance": {"range": SensorRange(0, 300000), "type": float},
        "ts": {"type": datetime.datetime},
    }

    valid_ranges = {
        k: extra_data_info[k]["range"] for k in extra_data_info if k != "ts"
    }
    numeric_columns = [
        "precipitation",
        "illuminance",
        "irradiance",
        "windspeedgust",
        "humidity",
        "temperature",
        "windspeedavg",
    ]
    categorical_columns = []

    return DataSource(
        df,
        time_column="ts",
        valid_ranges=valid_ranges,
        categorical_columns=categorical_columns,
        numeric_columns=numeric_columns,
    )

def load_egm2(path=None,timecol=None,delimiter=","):
    if not path:
        path = os.path.join(_DATA_FOLDER_ROOT, "low_cost_weather_station/")

    if not timecol:
        timecol="observedAt"

    metric_vals=['mm','cm','%','°C',' m']
    df = pd.read_csv(path,delimiter=delimiter)

    time = df[timecol].values
    
    # cols = {d[k].columns[1]: d[k][d[k].columns[1]] for k in d}
    df["ts"] = time
    df=df.drop(timecol,axis=1)
    for c in df.columns:
        temp_dtype=df[c].dtype
        df[c]=df[c].astype(str)
        tmp=df[c].str.contains('|'.join(metric_vals))
        if tmp.sum()/len(tmp)>0.1:

            df[c]=df[c].apply(lambda x: float(x.split(" ")[0]))
            df[c]=df[c].astype(float)
        else:
            df[c]=df[c].astype(temp_dtype)

    df["ts"] = pd.to_datetime(df["ts"])

    SensorRange = namedtuple("SensorRange", "min max")

    extra_data_info = {
        #  "windDirection": {
        #     "range": SensorRange(0, 50),
        #     # "Accuracy": "complicated",
        #     "type": float,
        # },
        # "illuminance": {"range": SensorRange(0, 300000), "type": float},
        "ts": {"type": datetime.datetime},
    }

    valid_ranges = {
        k: extra_data_info[k]["range"] for k in extra_data_info if k != "ts"
    }
    numeric_columns = [c for c in df.columns if (df[c].dtype==float or df[c].dtype==int)]

    categorical_columns = [c for c in df.columns if (df[c].dtype=="object")]

    return DataSource(
        df,
        time_column="ts",
        valid_ranges=valid_ranges,
        categorical_columns=categorical_columns,
        numeric_columns=numeric_columns,
    )



def load_santander_statuses(path=None):
    """
        Example FleetVehicleStatus:

        {
      "id": "urn:ngsi-ld:FleetVehicleStatus:santander:5",
      "type": "FleetVehicleStatus",
      "battery": {
        "type": "Property",
        "value": 34.81,
        "unitCode": "P1"
      },
      "dateModified": {
        "type": "TemporalProperty",
        "value": "2023-06-20T08:15:53.250395Z"
      },
      "location": {
        "type": "GeoProperty",
        "value": {
          "type": "Point",
          "coordinates": [
            -3.7847968270082366,
            43.46318315537095
          ]
        }
      },
      "speed": {
        "type": "Property",
        "value": 22.3,
        "unitCode": "KMH"
      },
      "@context": "https://raw.githubusercontent.com/SALTED-Project/contexts/main/wrapped_contexts/fleetvehiclestatus-context.jsonld"
    }

        Example BikeLaneIncident

        {
      "id": "urn:ngsi-ld:BikeLaneIncident:santander:5:18922",
      "type": "BikeLaneIncident",
      "incidentType": {
        "type": "Property",
        "value": "obstacle"
      },
      "dateObserved": {
        "type": "TemporalProperty",
        "value": "2023-06-20T08:19:19.508615Z"
      },
      "location": {
        "type": "GeoProperty",
        "value": {
          "type": "Point",
          "coordinates": [
            -3.7877879036906923,
            43.462130346359714
          ]
        }
      },

    """
    if not path:
        path = os.path.join(_DATA_FOLDER_ROOT, "dataset_SDR_example.jsonld")
    string = open(path, "r").read()
    arr = eval(string)
    _dicts = []

    def get_dt(x):
        return datetime.datetime.strptime(x, "%Y-%m-%dT%H:%M:%S.%fZ")

    types = set()
    for x in arr:
        if x["type"] == "FleetVehicleStatus":
            _dicts.append(
                {
                    "battery": x["battery"]["value"],
                    "datetime": get_dt(x["dateModified"]["value"]),
                    "location-x": x["location"]["value"]["coordinates"][0],
                    "location-y": x["location"]["value"]["coordinates"][1],
                    "speed": x["speed"]["value"],
                    "id": x["id"],
                }
            )
    df = pd.DataFrame(_dicts)
    df["datetime"] = pd.to_datetime(df["datetime"])
    df = DataSource(
        df,
        time_column="datetime",
        categorical_columns=["id"],
        numeric_columns=["battery", "location-x", "location-y", "speed"],
    )
    df._id_column = None
    return df


def load_steam():
    path = os.path.join(_DATA_FOLDER_ROOT, "steam-200k.csv")
    df = pd.read_csv(path, names=["user_id", "name", "purchas", "_1", "_2"])

    train_path = path = os.path.join(_DATA_FOLDER_ROOT, "dedupe_steam_train.json")
    train = eval(open(train_path, "r").read())

    _match = [[] for i in range(len(df))]
    _distinct = [[] for i in range(len(df))]
    df["id"] = np.arange(len(df))
    df["_id"] = df["id"].copy()

    for match in train["match"]:
        v = match["__value__"]
        print(v[0]["id"])
        _match[int(v[0]["id"])].append(v[1]["id"])

    for distinct in train["distinct"]:
        v = distinct["__value__"]
        _distinct[int(v[0]["id"])].append(v[1]["id"])

    df["_match"] = _match
    df["_distinct"] = _distinct

    return DataFrame(df)


def load_fodor_zagat(fodor_path=None, zagat_path=None):
    fodor_path = os.path.join(_DATA_FOLDER_ROOT, "fodorzagat/fodors.csv")
    zagat_path = os.path.join(_DATA_FOLDER_ROOT, "fodorzagat/zagats.csv")
    perfect_path = os.path.join(
        _DATA_FOLDER_ROOT, "fodorzagat/fodors-zagats_perfectMapping.csv"
    )

    fodor = pd.read_csv(fodor_path)
    zagat = pd.read_csv(zagat_path)
    perfect = pd.read_csv(perfect_path)

    df = pd.concat([fodor, zagat], axis=0, ignore_index=True)

    return df, perfect


def load_fv(folder_path=None):
    if not folder_path:
        folder_path = os.path.join(_DATA_FOLDER_ROOT, "FV")
    ecocounter_path = os.path.join(
        folder_path, "CSV2_1/EcoCounter_observations/ecocounter_observations.csv"
    )
    df = pd.read_csv(ecocounter_path)

    def get_dt(x):
        x = str(x)
        year = int(x[:4])
        month = int(x[4:6])
        day = int(x[6:8])
        hour = int(x[8:10])
        return datetime.datetime(year=year, month=month, day=day, hour=hour)

    df = pd.read_csv(ecocounter_path)
    df = df.drop("direction", axis=1)
    df["datetime"] = df["datetime"].apply(lambda x: get_dt(x))
    ecocounter = DataSource(
        df,
        categorical_columns=[
            "id",
#            "direction",
            "unit",
            "typeofmeasurement",
            "vehicletype",
            "source",
        ],
        numeric_columns=["value", "phenomenondurationseconds"],
        time_column="datetime",
    )

    info_path = os.path.join(
        folder_path, "CSV2_2/InfoTripla_observations/infotripla_observations.csv"
    )
    df = pd.read_csv(info_path)
    df["datetime"] = df["datetime"].apply(lambda x: get_dt(x))
    info = DataSource(
        df,
        categorical_columns=[
            "id",
            "direction",
            "unit",
            "typeofmeasurement",
            "vehicletype",
            "source",
        ],
        numeric_columns=["value", "phenomenondurationseconds"],
        time_column="datetime",
    )

    m680_path = os.path.join(
        folder_path, "CSV2_3/m680_observations/m680_observations.csv"
    )
    df = pd.read_csv(m680_path)
    df["datetime"] = df["datetime"].apply(lambda x: get_dt(x))

    m680 = DataSource(
        df,
        categorical_columns=[
            "id",
            "direction",
            "unit",
            "typeofmeasurement",
            "vehicletype",
            "source",
        ],
        numeric_columns=["value", "phenomenondurationseconds"],
        time_column="datetime",
    )

    return ecocounter, info, m680
