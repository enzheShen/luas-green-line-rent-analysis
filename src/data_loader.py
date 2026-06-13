"""Download the raw datasets and build the Luas station metadata file.

Data sources:
  - RTB Average Monthly Rent Report (table RIA02), published through the
    CSO PxStat API: https://data.cso.ie (annual, 2008 onwards)
  - Luas stop locations from Transport Infrastructure Ireland:
    https://data.tii.ie/Datasets/Luas/StopLocations/

Usage:
    python src/data_loader.py            # download (if needed) and build everything
    python src/data_loader.py --force    # re-download even if raw files exist
"""

import argparse
import csv
import math
from pathlib import Path

import pandas as pd
import requests

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
STATIONS_CSV = PROJECT_ROOT / "data" / "luas_stations.csv"

RTB_URL = "https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadDataset/RIA02/CSV/1.0/en"
LUAS_STOPS_URL = "https://data.tii.ie/Datasets/Luas/StopLocations/luas-stops.txt"

RTB_RAW = RAW_DIR / "rtb_ria02_raw.csv"
LUAS_RAW = RAW_DIR / "luas_stops_raw.txt"
RTB_DUBLIN = PROCESSED_DIR / "rtb_rent_dublin.csv"

GREEN_LINE_ID = 2
CITY_CENTRE_STOP = "St. Stephen's Green"

# Per-station metadata that isn't in the TII file.
# travel_min = scheduled journey time to St. Stephen's Green (Luas timetable).
# rtb_location_area = the closest suburb-level location in the RTB report
#   (these series run 2008-2025);
# rtb_location_district = the Dublin postal district (only published up to
#   2021, when the RTB changed its reporting areas - useful as a smoother
#   fallback for the earlier years).
STATION_META = {
    "St. Stephen's Green": (0, "Charlemont Street, Dublin 2", "Dublin 2"),
    "Harcourt": (2, "Charlemont Street, Dublin 2", "Dublin 2"),
    "Charlemont": (4, "Charlemont Street, Dublin 2", "Dublin 2"),
    "Ranelagh": (7, "Ranelagh, Dublin 6", "Dublin 6"),
    "Beechwood": (9, "Ranelagh, Dublin 6", "Dublin 6"),
    "Cowper": (11, "Ranelagh, Dublin 6", "Dublin 6"),
    "Milltown": (13, "Milltown, Dublin 6", "Dublin 6"),
    "Windy Arbour": (15, "Churchtown, Dublin 14", "Dublin 14"),
    "Dundrum": (17, "Dundrum, Dublin 16", "Dublin 14"),
    "Balally": (19, "Dundrum, Dublin 16", "Dublin 16"),
    "Kilmacud": (21, "Stillorgan, Dublin", "Dublin 14"),
    "Stillorgan": (22, "Stillorgan, Dublin", "Dublin 18"),
    "Sandyford": (24, "Sandyford, Dublin 18", "Dublin 18"),
    "Central Park": (26, "Leopardstown, Dublin 18", "Dublin 18"),
    "Glencairn": (28, "Leopardstown, Dublin 18", "Dublin 18"),
    "The Gallops": (29, "Leopardstown, Dublin 18", "Dublin 18"),
    "Leopardstown Valley": (31, "Leopardstown, Dublin 18", "Dublin 18"),
    "Ballyogan Wood": (33, "Carrickmines, Dublin 18", "Dublin 18"),
    "Racecourse": (34, "Leopardstown, Dublin 18", "Dublin 18"),
    "Carrickmines": (36, "Carrickmines, Dublin 18", "Dublin 18"),
    "Brennanstown": (37, "Cabinteely, Dublin 18", "Dublin 18"),
    "Laughanstown": (39, "Cabinteely, Dublin 18", "Dublin 18"),
    "Cherrywood": (41, "Cabinteely, Dublin 18", "Dublin 18"),
    "Brides Glen": (42, "Shankill, Dublin", "Dublin 18"),
}


def download(url, dest, force=False):
    if dest.exists() and not force:
        print(f"  already have {dest.name}, skipping download")
        return
    print(f"  downloading {url}")
    resp = requests.get(url, timeout=300)
    resp.raise_for_status()
    dest.write_bytes(resp.content)
    print(f"  saved {dest.name} ({len(resp.content) / 1e6:.1f} MB)")


def haversine_km(lat1, lon1, lat2, lon2):
    """Great-circle distance between two points, in km."""
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = p2 - p1
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def build_stations_csv():
    """Filter the TII stop file down to the Green Line and add our metadata."""
    stops = pd.read_csv(LUAS_RAW, sep="\t", encoding="utf-8-sig")
    green = stops[stops["LineID"] == GREEN_LINE_ID].copy()
    green = green.sort_values("SortOrder").reset_index(drop=True)

    missing = set(green["Name"]) - set(STATION_META)
    if missing:
        raise ValueError(f"No metadata for stops: {missing}")
    if len(green) != len(STATION_META):
        raise ValueError(
            f"Expected {len(STATION_META)} Green Line stops, got {len(green)}"
        )

    centre = green[green["Name"] == CITY_CENTRE_STOP].iloc[0]
    rows = []
    for seq, stop in green.iterrows():
        travel_min, area, district = STATION_META[stop["Name"]]
        rows.append({
            "stop_sequence": seq,
            "station": stop["Name"],
            "latitude": round(stop["Latitude"], 6),
            "longitude": round(stop["Longitude"], 6),
            "distance_km_to_centre": round(
                haversine_km(stop["Latitude"], stop["Longitude"],
                             centre["Latitude"], centre["Longitude"]), 2),
            "travel_min_to_centre": travel_min,
            "rtb_location_area": area,
            "rtb_location_district": district,
            "park_and_ride": int(stop["IsParkAndRide"]),
        })

    df = pd.DataFrame(rows)
    df.to_csv(STATIONS_CSV, index=False)
    print(f"  wrote {STATIONS_CSV.relative_to(PROJECT_ROOT)} ({len(df)} stations)")
    return df


def filter_rtb_dublin(stations):
    """Keep only the RTB rows for locations our stations map to."""
    wanted = set(stations["rtb_location_area"].dropna())
    wanted |= set(stations["rtb_location_district"])
    wanted.add("Dublin")  # county-wide benchmark

    rtb = pd.read_csv(RTB_RAW, encoding="utf-8-sig", low_memory=False)
    rtb = rtb.rename(columns={
        "Year": "year",
        "Number of Bedrooms": "bedrooms",
        "Property Type": "property_type",
        "Location": "location",
        "VALUE": "avg_rent",
    })
    cols = ["year", "bedrooms", "property_type", "location", "avg_rent"]
    dublin = rtb.loc[rtb["location"].isin(wanted), cols].copy()

    found = set(dublin["location"])
    if wanted - found:
        raise ValueError(f"RTB locations not found in RIA02: {wanted - found}")

    dublin.to_csv(RTB_DUBLIN, index=False)
    print(f"  wrote {RTB_DUBLIN.relative_to(PROJECT_ROOT)} "
          f"({len(dublin)} rows, {len(found)} locations, "
          f"{dublin['year'].min()}-{dublin['year'].max()})")
    return dublin


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true",
                        help="re-download raw files even if they exist")
    args = parser.parse_args()

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    print("1. Downloading raw data")
    download(RTB_URL, RTB_RAW, force=args.force)
    download(LUAS_STOPS_URL, LUAS_RAW, force=args.force)

    print("2. Building station metadata")
    stations = build_stations_csv()

    print("3. Filtering RTB data to relevant Dublin locations")
    filter_rtb_dublin(stations)

    print("Done.")


if __name__ == "__main__":
    main()
