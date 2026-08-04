# Windows Codex handoff — Power BI final stage

## Project

Repository: `https://github.com/enzheShen/luas-green-line-rent-analysis`

Goal: finish the Power BI Desktop deliverable for a portfolio project analysing registered rents near all 24 stops on Dublin's Luas Green Line.

The Mac/Python work is already complete. Do not rebuild the data pipeline on Windows unless a real data issue is found.

## Completed work

- RTB RIA02 and TII data pipeline
- 24-stop station metadata and area mapping
- SQLite schema and 17 analytical SQL queries
- Two executed notebooks with regression and visualisations
- Public Streamlit app: `https://luas-green-line-rent-explorer.streamlit.app/`
- Excel executive report
- Complete project README
- Power BI-ready CSV, theme and step-by-step guide

All completed work is committed to `main` on GitHub.

## Files to use on Windows

- `powerbi/luas_rent_powerbi.csv` — import this into Power BI Desktop
- `powerbi/luas_theme.json` — import from View → Themes → Browse for themes
- `powerbi/README_powerbi_guide.md` — follow this build guide

The CSV already contains 6,960 rows, 24 stations, years 2008–2025, coordinates, commute minutes, RTB area, rent, Dublin benchmark and percentage difference. Python is not required on Windows.

## Main analytical story

Use the default report filters:

- Year: `2025`
- Bedrooms: `1 to 2 bed`
- Property type: `All property types`

Key verified results:

- City-centre rent: €2,118.72
- Cheapest station: Brides Glen, €1,772.20
- Dearest station: Windy Arbour, €2,412.45
- Ranelagh rent: €1,783.61, €335 below the city-centre benchmark
- Largest outward price jump: Cowper → Milltown, about €396
- Rent gradient: approximately -€1.44 per additional commute minute
- R²: approximately 0.01, so commute time barely explains rent variation

## Required Power BI output

Build one polished report page with:

1. Three slicers: year, bedrooms and property type
2. Four KPI cards: city-centre rent, cheapest rent, dearest rent and vs Dublin
3. Station map using latitude and longitude
4. Horizontal bar chart of rent by station
5. Green Line versus Dublin historical line chart
6. Rent versus commute scatter chart with a trend line

Use explicit DAX measures rather than summing the raw rent column. The exact measures and click-by-click instructions are in `README_powerbi_guide.md`.

## Files to create

Save these inside the cloned repository:

```text
powerbi/dashboard.pbix
powerbi/screenshots/dashboard_overview.png
powerbi/screenshots/map.png
powerbi/screenshots/gradient.png
```

After visually checking the report, add the overview screenshot to the root README, then commit and push the files to `main`.

Suggested commit message:

```text
Add Power BI dashboard and report screenshots
```

## Prompt to give Codex on Windows

```text
Read powerbi/WINDOWS_CODEX_HANDOFF.md and powerbi/README_powerbi_guide.md. The project is complete except for the final Power BI Desktop dashboard. Guide me through building it with the existing powerbi/luas_rent_powerbi.csv, verify each visual from screenshots, then help me save dashboard.pbix, add README screenshots, commit and push the result. Do not rebuild the Python data pipeline.
```
