-- Q6. Which area on the line has grown fastest over the last decade?
-- Techniques: conditional aggregation to pick two years out of a series

SELECT
    location,
    ROUND(MAX(CASE WHEN year = 2015 THEN avg_rent END)) AS rent_2015,
    ROUND(MAX(CASE WHEN year = 2025 THEN avg_rent END)) AS rent_2025,
    ROUND(100.0 * (MAX(CASE WHEN year = 2025 THEN avg_rent END)
                 - MAX(CASE WHEN year = 2015 THEN avg_rent END))
               / MAX(CASE WHEN year = 2015 THEN avg_rent END), 1) AS growth_pct
FROM rents
WHERE bedrooms = 'All bedrooms'
  AND property_type = 'All property types'
  AND location IN (SELECT DISTINCT rtb_location_area FROM stations)
GROUP BY location
ORDER BY growth_pct DESC;
