-- Q14. Has the pecking order changed? Each area's expensiveness rank in
--      2015 vs 2025.
-- Techniques: two CTEs with RANK(), joining the two ranked results

WITH r2015 AS (
    SELECT location, RANK() OVER (ORDER BY avg_rent DESC) AS rank_2015
    FROM rents
    WHERE year = 2015
      AND bedrooms = 'All bedrooms'
      AND property_type = 'All property types'
      AND location IN (SELECT DISTINCT rtb_location_area FROM stations)
),
r2025 AS (
    SELECT location, RANK() OVER (ORDER BY avg_rent DESC) AS rank_2025
    FROM rents
    WHERE year = 2025
      AND bedrooms = 'All bedrooms'
      AND property_type = 'All property types'
      AND location IN (SELECT DISTINCT rtb_location_area FROM stations)
)
SELECT
    location,
    rank_2015,
    rank_2025,
    rank_2015 - rank_2025 AS places_moved_up
FROM r2015
JOIN r2025 USING (location)
ORDER BY rank_2025;
