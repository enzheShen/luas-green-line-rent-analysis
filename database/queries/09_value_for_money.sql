-- Q9. Value for money: how much rent do you save per extra commuting
--     minute at each station?
-- Techniques: CTE benchmark, CROSS JOIN, computed metrics, edge-case filter

WITH centre AS (
    SELECT avg_rent AS centre_rent
    FROM station_rents
    WHERE station = 'St. Stephen''s Green'
      AND year = 2025
      AND bedrooms = '1 to 2 bed'
      AND property_type = 'All property types'
)
SELECT
    sr.station,
    sr.travel_min_to_centre AS commute_min,
    ROUND(sr.avg_rent) AS rent_1to2bed,
    ROUND(c.centre_rent - sr.avg_rent) AS monthly_saving,
    ROUND((c.centre_rent - sr.avg_rent) / sr.travel_min_to_centre, 1) AS saving_per_minute
FROM station_rents sr
CROSS JOIN centre c
WHERE sr.year = 2025
  AND sr.bedrooms = '1 to 2 bed'
  AND sr.property_type = 'All property types'
  AND sr.travel_min_to_centre > 0   -- the city centre itself has no commute
ORDER BY saving_per_minute DESC;
