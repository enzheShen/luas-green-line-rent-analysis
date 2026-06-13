-- Q8. The "price cliff": where is the biggest rent jump between two
--     neighbouring stations?
-- Techniques: LAG() over the physical stop order, CTE, ABS()

WITH steps AS (
    SELECT
        stop_sequence,
        station,
        LAG(station)  OVER (ORDER BY stop_sequence) AS previous_station,
        avg_rent,
        avg_rent - LAG(avg_rent) OVER (ORDER BY stop_sequence) AS step_change
    FROM station_rents
    WHERE year = 2025
      AND bedrooms = '1 to 2 bed'   -- the slice published for every area
      AND property_type = 'All property types'
)
SELECT
    previous_station || ' -> ' || station AS between_stops,
    ROUND(step_change) AS rent_change_eur
FROM steps
WHERE step_change IS NOT NULL
ORDER BY ABS(step_change) DESC;
