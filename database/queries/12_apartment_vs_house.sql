-- Q12. Is an apartment cheaper than a house in the same area? (2025)
-- Techniques: conditional aggregation over property types, NULL handling
--
-- Suburb-level RTB data gets sparse once sliced by property type, so some
-- cells come back NULL - that is the data, not a bug. The RTB suppresses
-- figures where there are too few tenancies to report safely.

SELECT
    location,
    ROUND(MAX(CASE WHEN property_type = 'Apartment'           THEN avg_rent END)) AS apartment,
    ROUND(MAX(CASE WHEN property_type = 'Semi detached house' THEN avg_rent END)) AS semi_detached,
    ROUND(MAX(CASE WHEN property_type = 'Terrace house'       THEN avg_rent END)) AS terrace
FROM rents
WHERE year = 2025
  AND bedrooms = 'All bedrooms'
  AND location IN (SELECT DISTINCT rtb_location_area FROM stations)
GROUP BY location
ORDER BY apartment DESC;
