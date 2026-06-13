-- Q3. How has rent on the line moved each year compared with Dublin overall?
-- Techniques: two CTEs, JOIN ... USING, GROUP BY
--
-- The line average weights each *station* equally, so an area with several
-- stops (e.g. Leopardstown) counts more. That is intentional: it represents
-- the average stop on the line, not the average suburb.

WITH line AS (
    SELECT year, AVG(avg_rent) AS line_avg
    FROM station_rents
    WHERE bedrooms = 'All bedrooms'
      AND property_type = 'All property types'
    GROUP BY year
),
county AS (
    SELECT year, avg_rent AS dublin_avg
    FROM rents
    WHERE location = 'Dublin'
      AND bedrooms = 'All bedrooms'
      AND property_type = 'All property types'
)
SELECT
    year,
    ROUND(line_avg)   AS line_avg,
    ROUND(dublin_avg) AS dublin_avg,
    ROUND(100.0 * (line_avg - dublin_avg) / dublin_avg, 1) AS premium_pct
FROM line
JOIN county USING (year)
ORDER BY year;
