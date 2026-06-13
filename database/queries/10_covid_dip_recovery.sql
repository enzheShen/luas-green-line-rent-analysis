-- Q10. What did Covid do to rents on the line, and have they recovered?
-- Techniques: conditional aggregation across three snapshot years

SELECT
    location,
    ROUND(MAX(CASE WHEN year = 2019 THEN avg_rent END)) AS pre_covid_2019,
    ROUND(MAX(CASE WHEN year = 2021 THEN avg_rent END)) AS covid_2021,
    ROUND(MAX(CASE WHEN year = 2025 THEN avg_rent END)) AS now_2025,
    ROUND(100.0 * (MAX(CASE WHEN year = 2021 THEN avg_rent END)
                 - MAX(CASE WHEN year = 2019 THEN avg_rent END))
               / MAX(CASE WHEN year = 2019 THEN avg_rent END), 1) AS covid_change_pct
FROM rents
WHERE bedrooms = 'All bedrooms'
  AND property_type = 'All property types'
  AND location IN (SELECT DISTINCT rtb_location_area FROM stations)
GROUP BY location
ORDER BY covid_change_pct;
