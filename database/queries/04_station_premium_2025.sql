-- Q4. Which stations sit above / below the Dublin county average in 2025?
-- Techniques: CTE, CROSS JOIN to a one-row benchmark, percentage maths

WITH benchmark AS (
    SELECT avg_rent AS dublin_avg
    FROM rents
    WHERE location = 'Dublin'
      AND year = 2025
      AND bedrooms = 'All bedrooms'
      AND property_type = 'All property types'
)
SELECT
    sr.station,
    ROUND(sr.avg_rent)  AS rent_2025,
    ROUND(b.dublin_avg) AS dublin_avg,
    ROUND(100.0 * (sr.avg_rent - b.dublin_avg) / b.dublin_avg, 1) AS vs_dublin_pct
FROM station_rents sr
CROSS JOIN benchmark b
WHERE sr.year = 2025
  AND sr.bedrooms = 'All bedrooms'
  AND sr.property_type = 'All property types'
ORDER BY vs_dublin_pct DESC;
