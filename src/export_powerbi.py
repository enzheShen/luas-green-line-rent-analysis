"""Export a single, clean, Power BI-friendly CSV.

Power BI imports a flat table far more reliably than a SQLite file, so this
flattens the station_rents view (rent + station attributes in one row) and
adds the city-centre and Dublin-county benchmarks as extra columns that make
DAX measures easy to write.

    python src/export_powerbi.py
"""

from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUT_CSV = PROJECT_ROOT / "powerbi" / "luas_rent_powerbi.csv"

import sys
sys.path.append(str(PROJECT_ROOT / "src"))
from sql_utils import run_sql  # noqa: E402


def build_export():
    # One row per station x year x bedrooms x property type, with the
    # station's coordinates and commute time already joined on.
    df = run_sql("""
        SELECT
            sr.stop_sequence,
            sr.station,
            s.latitude,
            s.longitude,
            sr.distance_km_to_centre,
            sr.travel_min_to_centre,
            CASE sr.park_and_ride WHEN 1 THEN 'Yes' ELSE 'No' END AS park_and_ride,
            sr.location           AS rtb_area,
            sr.year,
            sr.bedrooms,
            sr.property_type,
            sr.avg_rent
        FROM station_rents sr
        JOIN stations s USING (stop_sequence)
        ORDER BY sr.year, sr.stop_sequence
    """)

    # Dublin county benchmark for the same slice/year - lets Power BI show a
    # "rent vs county" measure without a second table.
    dublin = run_sql("""
        SELECT year, bedrooms, property_type, avg_rent AS dublin_avg
        FROM rents
        WHERE location = 'Dublin'
    """)
    df = df.merge(dublin, on=["year", "bedrooms", "property_type"], how="left")
    df["vs_dublin_pct"] = (
        100 * (df["avg_rent"] - df["dublin_avg"]) / df["dublin_avg"]
    ).round(1)

    df.to_csv(OUT_CSV, index=False)
    print(f"wrote {OUT_CSV.relative_to(PROJECT_ROOT)} "
          f"({len(df):,} rows, {df['year'].nunique()} years, "
          f"{df['station'].nunique()} stations)")


if __name__ == "__main__":
    build_export()
