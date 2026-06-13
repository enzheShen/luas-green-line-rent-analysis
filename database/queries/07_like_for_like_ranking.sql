-- Q7. Rank every station by 1-2 bed rent - the like-for-like comparison.
-- Techniques: RANK() window function
--
-- Why fix the bedroom count? The headline 'all properties' average mixes
-- city-centre one-bed apartments with suburban four-bed houses, which
-- hides the distance effect (compare with query 01). '1 to 2 bed' is used
-- because it is the only controlled slice the RTB publishes for every
-- area on the line ('Two bed' alone is suppressed in the city centre).

SELECT
    RANK() OVER (ORDER BY avg_rent) AS cheapest_rank,
    station,
    location,
    travel_min_to_centre,
    ROUND(avg_rent) AS rent_1to2bed_2025
FROM station_rents
WHERE year = 2025
  AND bedrooms = '1 to 2 bed'
  AND property_type = 'All property types'
ORDER BY cheapest_rank;
