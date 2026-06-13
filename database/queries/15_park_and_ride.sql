-- Q15. Do stations with a park-and-ride differ in rent from those without?
-- Techniques: GROUP BY on a flag, CASE for labels, COUNT + AVG

SELECT
    CASE park_and_ride WHEN 1 THEN 'Park & ride' ELSE 'No park & ride' END AS station_type,
    COUNT(*)                            AS stations,
    ROUND(AVG(avg_rent))                AS avg_rent_1to2bed,
    ROUND(AVG(travel_min_to_centre), 1) AS avg_commute_min
FROM station_rents
WHERE year = 2025
  AND bedrooms = '1 to 2 bed'
  AND property_type = 'All property types'
GROUP BY park_and_ride;
