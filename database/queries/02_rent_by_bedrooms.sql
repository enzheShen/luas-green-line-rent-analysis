-- Q2. What does each bedroom count cost in every area on the line (2025)?
-- Techniques: GROUP BY, conditional aggregation (CASE inside an aggregate),
--             subquery with IN
--
-- NULLs are areas where the RTB suppresses the figure (too few tenancies).
-- '1 to 2 bed' is the only slice published for every area, which is why
-- the like-for-like queries (07-09, 15-17) standardise on it.

SELECT
    location,
    ROUND(MAX(CASE WHEN bedrooms = 'One bed'    THEN avg_rent END)) AS one_bed,
    ROUND(MAX(CASE WHEN bedrooms = '1 to 2 bed' THEN avg_rent END)) AS one_to_two_bed,
    ROUND(MAX(CASE WHEN bedrooms = 'Two bed'    THEN avg_rent END)) AS two_bed,
    ROUND(MAX(CASE WHEN bedrooms = 'Three bed'  THEN avg_rent END)) AS three_bed
FROM rents
WHERE year = 2025
  AND property_type = 'All property types'
  AND location IN (SELECT DISTINCT rtb_location_area FROM stations)
GROUP BY location
ORDER BY one_to_two_bed;
