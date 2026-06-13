-- Q13. Smooth the noisy yearly series with a 3-year rolling average.
-- Techniques: AVG() window function with a ROWS frame

SELECT
    location,
    year,
    ROUND(avg_rent) AS avg_rent,
    ROUND(AVG(avg_rent) OVER (PARTITION BY location ORDER BY year
                              ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)) AS rolling_3yr
FROM rents
WHERE bedrooms = 'All bedrooms'
  AND property_type = 'All property types'
  AND location IN (SELECT DISTINCT rtb_location_area FROM stations)
ORDER BY location, year;
