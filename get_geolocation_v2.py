import time
from pathlib import Path
from random import randint

import geopy
import pandas as pd
from geopy.exc import (ConfigurationError, GeocoderParseError,
                       GeocoderQueryError, GeocoderQuotaExceeded,
                       GeocoderServiceError, GeocoderTimedOut,
                       GeocoderUnavailable)
from tqdm import tqdm

GEOCODERS_LIST = list(geopy.geocoders.SERVICE_TO_GEOCODER.keys())


def dynamic_geocoder(address: str, geocoder_str: str):
    user_agent = 'user_{}'.format(randint(152, 98383))
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
        print(f"Intentando con {geocoder_str}")
    except KeyError:
        print("We tried all geocoders :( ")
        # Dejamos este como default
        geocoder_str = "nominatim"
    return geocoder_str


def get_lat_long(df: pd.DataFrame, col: str):
    latitude = []
    longitude = []
    address = []

    geocoder_str = get_geocoder_str(GEOCODERS_LIST)

    for addr in tqdm(df[col]):
        try:
            lat, lon = dynamic_geocoder(addr, geocoder_str)
        except (GeocoderTimedOut, GeocoderServiceError, GeocoderQueryError,
                GeocoderQuotaExceeded, ConfigurationError,
                GeocoderParseError, GeocoderUnavailable) as e:
            print(f"Geocode error: {e} for {geocoder_str}. /n Trying another")
            lat, lon = None, None
            geocoder_str = get_geocoder_str(GEOCODERS_LIST)

        latitude.append(lat)
        longitude.append(lon)
        address.append(addr)
        time.sleep(0.3)

    return latitude, longitude, address


if __name__ == "__main__":
    path = Path(".")
    df = pd.read_csv(path / "sample_small_data.csv")
    lat, lon, addr = get_lat_long(df, "delivery_address")
    results = pd.DataFrame({'lat': lat, 'lon': lon, 'address': addr})
    df_final = pd.concat([df, results], axis=1)
    df_final.to_csv(path / "out.csv", index=False)
