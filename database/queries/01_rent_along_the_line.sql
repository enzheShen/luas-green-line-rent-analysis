-- Q1. How does average rent vary along the Green Line right now?
-- Techniques: view (pre-built JOIN), WHERE, ORDER BY
--
-- Uses 'All bedrooms / All property types', the headline figure the RTB
-- publishes. Spoiler: the line looks surprisingly flat this way - see
-- query 07 for why controlling for bedrooms matters.

SELECT
    stop_sequence,
    station,
    location              AS rtb_area,
    travel_min_to_centre,
    ROUND(avg_rent)       AS avg_rent_2025
FROM station_rents
WHERE year = 2025
  AND bedrooms = 'All bedrooms'
  AND property_type = 'All property types'
ORDER BY stop_sequence;
