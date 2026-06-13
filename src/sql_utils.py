"""Build and query the project's SQLite database.

The database is rebuilt from the CSVs in data/, so it never needs to be
committed - anyone can recreate it with:

    python src/sql_utils.py --build

Other usage:
    python src/sql_utils.py --run 08      # run database/queries/08_*.sql
    python src/sql_utils.py --run-all     # run every query, print a preview
"""

import argparse
import sqlite3
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "database" / "rent_data.db"
SCHEMA_PATH = PROJECT_ROOT / "database" / "schema.sql"
QUERIES_DIR = PROJECT_ROOT / "database" / "queries"
STATIONS_CSV = PROJECT_ROOT / "data" / "luas_stations.csv"
RENTS_CSV = PROJECT_ROOT / "data" / "processed" / "rtb_rent_dublin.csv"


def get_engine():
    """SQLAlchemy engine for the project database (used by pandas)."""
    return create_engine(f"sqlite:///{DB_PATH}")


def build_database():
    """(Re)create the database from schema.sql and the data CSVs."""
    stations = pd.read_csv(STATIONS_CSV)
    # Rows with no published rent figure carry no information, so they are
    # dropped here rather than handled in every single query.
    rents = pd.read_csv(RENTS_CSV).dropna(subset=["avg_rent"])

    con = sqlite3.connect(DB_PATH)
    try:
        con.executescript(SCHEMA_PATH.read_text())
        stations.to_sql("stations", con, if_exists="append", index=False)
        rents.to_sql("rents", con, if_exists="append", index=False)
        con.commit()
        n_stations = con.execute("SELECT COUNT(*) FROM stations").fetchone()[0]
        n_rents = con.execute("SELECT COUNT(*) FROM rents").fetchone()[0]
    finally:
        con.close()
    print(f"Built {DB_PATH.name}: {n_stations} stations, {n_rents} rent rows")


def run_sql(sql):
    """Run a SQL string and return the result as a DataFrame."""
    return pd.read_sql_query(sql, get_engine())


def find_query_file(prefix):
    matches = sorted(QUERIES_DIR.glob(f"{prefix}*.sql"))
    if not matches:
        raise FileNotFoundError(f"No query file starting with '{prefix}'")
    return matches[0]


def run_query_file(prefix):
    """Run one of the saved queries by its number, e.g. '08'."""
    return run_sql(find_query_file(prefix).read_text())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true", help="rebuild the database")
    parser.add_argument("--run", metavar="N", help="run query file N and print it")
    parser.add_argument("--run-all", action="store_true",
                        help="run every saved query and print a preview")
    args = parser.parse_args()

    if args.build:
        build_database()
    if args.run:
        df = run_query_file(args.run)
        print(df.to_string(index=False))
    if args.run_all:
        for path in sorted(QUERIES_DIR.glob("*.sql")):
            df = run_sql(path.read_text())
            print(f"\n=== {path.name} ({len(df)} rows) ===")
            print(df.head(8).to_string(index=False))
    if not (args.build or args.run or args.run_all):
        parser.print_help()


if __name__ == "__main__":
    main()
