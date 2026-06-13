-- Q16. The headline number: how many euro does one extra minute of commute
--      knock off a 1-2 bed rent? (simple least-squares fit, done in SQL)
-- Techniques: CTE, regression slope from aggregate formulas
--   slope = (avg(xy) - avg(x)avg(y)) / (avg(x^2) - avg(x)^2)
--
-- The Python notebook repeats this properly with scikit-learn (confidence
-- intervals etc.); matching numbers here is a nice cross-check.

WITH pts AS (
    SELECT
        travel_min_to_centre * 1.0 AS x,
        avg_rent                   AS y
    FROM station_rents
    WHERE year = 2025
      AND bedrooms = '1 to 2 bed'
      AND property_type = 'All property types'
)
SELECT
    COUNT(*) AS stations,
    ROUND((AVG(x * y) - AVG(x) * AVG(y))
        / (AVG(x * x) - AVG(x) * AVG(x)), 2) AS eur_per_commute_minute,
    ROUND(AVG(y) - (AVG(x * y) - AVG(x) * AVG(y))
                 / (AVG(x * x) - AVG(x) * AVG(x)) * AVG(x)) AS implied_centre_rent
FROM pts;
