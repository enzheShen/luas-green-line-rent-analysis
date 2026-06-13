-- Schema for the Luas Green Line rent database (SQLite).
-- Built by src/sql_utils.py from the CSVs in data/.
--
-- Two tables and one view:
--   stations      one row per Green Line stop (24 rows)
--   rents         one row per year x bedrooms x property type x RTB location
--   station_rents view joining the two, so most queries don't have to
--                 repeat the join

DROP VIEW IF EXISTS station_rents;
DROP TABLE IF EXISTS rents;
DROP TABLE IF EXISTS stations;

CREATE TABLE stations (
    stop_sequence         INTEGER PRIMARY KEY,  -- 0 = St. Stephen's Green
    station               TEXT    NOT NULL UNIQUE,
    latitude              REAL    NOT NULL,
    longitude             REAL    NOT NULL,
    distance_km_to_centre REAL    NOT NULL,
    travel_min_to_centre  INTEGER NOT NULL,
    rtb_location_area     TEXT    NOT NULL,     -- suburb-level RTB location (2008-2025)
    rtb_location_district TEXT    NOT NULL,     -- postal district (series ends 2021)
    park_and_ride         INTEGER NOT NULL CHECK (park_and_ride IN (0, 1))
);

CREATE TABLE rents (
    rent_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    year          INTEGER NOT NULL,
    bedrooms      TEXT    NOT NULL,  -- 'All bedrooms', 'One bed', 'Two bed', ...
    property_type TEXT    NOT NULL,  -- 'All property types', 'Apartment', ...
    location      TEXT    NOT NULL,  -- RTB location name
    avg_rent      REAL    NOT NULL   -- average monthly rent in euro
);

CREATE INDEX idx_rents_location_year ON rents (location, year);
CREATE INDEX idx_rents_slice ON rents (bedrooms, property_type);

CREATE VIEW station_rents AS
SELECT
    s.stop_sequence,
    s.station,
    s.distance_km_to_centre,
    s.travel_min_to_centre,
    s.park_and_ride,
    r.location,
    r.year,
    r.bedrooms,
    r.property_type,
    r.avg_rent
FROM stations s
JOIN rents r ON r.location = s.rtb_location_area;
