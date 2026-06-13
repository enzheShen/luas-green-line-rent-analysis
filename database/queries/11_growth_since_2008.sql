-- Q11. The full 18-year picture: each area's rent at the start and end of
--      its published series.
-- Techniques: FIRST_VALUE / LAST_VALUE window functions with an explicit
--             frame clause, SELECT DISTINCT

SELECT DISTINCT
    location,
    FIRST_VALUE(year)            OVER w  AS first_year,
    ROUND(FIRST_VALUE(avg_rent)  OVER w) AS start_rent,
    LAST_VALUE(year)             OVER w  AS last_year,
    ROUND(LAST_VALUE(avg_rent)   OVER w) AS end_rent,
    ROUND(100.0 * (LAST_VALUE(avg_rent) OVER w - FIRST_VALUE(avg_rent) OVER w)
               / FIRST_VALUE(avg_rent) OVER w, 1) AS total_growth_pct
FROM rents
WHERE bedrooms = 'All bedrooms'
  AND property_type = 'All property types'
  AND location IN (SELECT DISTINCT rtb_location_area FROM stations)
WINDOW w AS (PARTITION BY location ORDER BY year
             ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
ORDER BY total_growth_pct DESC;
