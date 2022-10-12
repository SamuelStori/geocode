import os
import sys
import time
from random import randint
from util import rs_conn
import geopy
import pandas as pd
from geopy.exc import (
    ConfigurationError,
    GeocoderParseError,
    GeocoderQueryError,
    GeocoderQuotaExceeded,
    GeocoderServiceError,
    GeocoderTimedOut,
    GeocoderUnavailable,
)
from tqdm import tqdm

sql_query = str(sys.argv[1])
col_name = str(sys.argv[2])
schema_rs = str(sys.argv[3])
table_rs = str(sys.argv[4])

GEOCODERS_LIST = list(geopy.geocoders.SERVICE_TO_GEOCODER.keys())


def dynamic_geocoder(address: str, geocoder_str: str):
    user_agent = "user_{}".format(randint(152, 98383))
    geocoder = geopy.geocoders.SERVICE_TO_GEOCODER[geocoder_str](user_agent=user_agent)
    location = geocoder.geocode(address)
    if location is not None:
        lat, lon = location.latitude, location.longitude
    else:
        lat, lon = None, None

    return lat, lon


def get_geocoder_str(geocoders_list: list) -> str:
    try:
        geocoder_str = geocoders_list.pop(0)
        print(f"Trying with {geocoder_str}:")
    except KeyError:
        print("All geocoders tried.")
        geocoder_str = "nominatim"
    return geocoder_str


def get_lat_long(df: pd.DataFrame, col: str):
    latitude = []
    longitude = []

    geocoder_str = get_geocoder_str(GEOCODERS_LIST)

    for addr in tqdm(df[col]):
        try:
            lat, lon = dynamic_geocoder(addr, geocoder_str)
        except (
            GeocoderTimedOut,
            GeocoderServiceError,
            GeocoderQueryError,
            GeocoderQuotaExceeded,
            ConfigurationError,
            GeocoderParseError,
            GeocoderUnavailable,
        ) as e:
            print(f"Geocode error: {e} for {geocoder_str}. \n Trying another")
            lat, lon = None, None
            geocoder_str = get_geocoder_str(GEOCODERS_LIST)

        latitude.append(lat)
        longitude.append(lon)

        time.sleep(0.3)

    df["latitude"] = latitude
    df["longitude"] = longitude

    return df


if __name__ == "__main__":
    rs = rs_conn.RS_CONN(rs_user=os.getenv("RS_USER"), rs_pass=os.getenv("RS_PASS"))
    rs.set_Conn()
    query_sample = open(f"./{sql_query}", "r").read()
    df = rs.get_result_df(query_sample)
    df = get_lat_long(df=df, col=col_name)

    print(f"Uploading to {schema_rs}.{table_rs} in Redshift")

    df.to_sql(
        schema=schema_rs,
        con=rs.engine,
        name=table_rs,
        if_exists="append",
        index=False,
        chunksize=1000,
        method="multi",
    )

    rs.conn.close()

    print("Upload finished")

