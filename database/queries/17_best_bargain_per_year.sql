-- Q17. Which station was the single cheapest on the line in every year?
-- Techniques: ROW_NUMBER() to pick the top row per group (the classic
--             "greatest-n-per-group" pattern)

WITH ranked AS (
    SELECT
        year,
        station,
        avg_rent,
        ROW_NUMBER() OVER (PARTITION BY year ORDER BY avg_rent) AS rn
    FROM station_rents
    WHERE bedrooms = '1 to 2 bed'
      AND property_type = 'All property types'
)
SELECT
    year,
    station         AS cheapest_station,
    ROUND(avg_rent) AS rent_1to2bed
FROM ranked
WHERE rn = 1
ORDER BY year;
