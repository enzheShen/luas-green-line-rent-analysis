-- Q5. Year-on-year rent growth for each area on the line.
-- Techniques: LAG() window function with PARTITION BY, named WINDOW clause

SELECT
    location,
    year,
    ROUND(avg_rent) AS avg_rent,
    ROUND(100.0 * (avg_rent - LAG(avg_rent) OVER w)
               / LAG(avg_rent) OVER w, 1) AS yoy_pct
FROM rents
WHERE bedrooms = 'All bedrooms'
  AND property_type = 'All property types'
  AND location IN (SELECT DISTINCT rtb_location_area FROM stations)
WINDOW w AS (PARTITION BY location ORDER BY year)
ORDER BY location, year;
