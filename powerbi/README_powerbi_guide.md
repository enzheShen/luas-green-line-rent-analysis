# Building the Power BI dashboard — step by step

This guide assumes you have **never opened Power BI before**. Follow it top
to bottom and you'll end up with a `dashboard.pbix` file and the screenshots
the project README needs.

Power BI Desktop is **Windows-only and free**, so do this part on your
Windows PC. Everything else in the project stays on the Mac; you only need
to move one CSV across.

---

## 0. What you're about to build

A single report page with:

- three **slicers** (Year, Bedrooms, Property type) to filter everything
- four **KPI cards** (city-centre rent, cheapest stop, dearest stop, vs Dublin)
- a **map** of the line, stations coloured by rent
- a **bar chart** of rent per station
- a **line chart** comparing the line to the Dublin county average over time
- a **scatter** of rent vs commute time (the "no gradient" finding)

It mirrors the Streamlit app, but in the tool Irish employers actually ask
for.

---

## 1. Install Power BI Desktop

1. On the Windows PC, open the **Microsoft Store**, search **"Power BI
   Desktop"**, click **Get / Install**. (Or download from
   `https://powerbi.microsoft.com/desktop` — the Store version auto-updates,
   prefer it.)
2. Launch it. Close the start-up splash/sign-in pop-up — you do **not** need
   an account to build and save a report locally.

---

## 2. Get the data onto Windows

You only need one file: **`powerbi/luas_rent_powerbi.csv`** (already in the
repo, 6,960 rows). Two ways:

- **Easiest:** on the Windows PC, go to your GitHub repo in a browser →
  `powerbi/luas_rent_powerbi.csv` → **Download raw file**.
- Or clone the whole repo on Windows with `git clone`.

> If you ever change the analysis, regenerate this CSV on the Mac with
> `python src/export_powerbi.py` and re-download it.

---

## 3. Load the data

1. **Home → Get data → Text/CSV → Connect**, pick the CSV.
2. In the preview window, check the column types look right, then click
   **Transform Data** (not "Load") to open Power Query — we'll fix types
   properly.
3. In Power Query, confirm each column's type (click the icon left of each
   header):
   - `latitude`, `longitude`, `avg_rent`, `dublin_avg`, `vs_dublin_pct`,
     `distance_km_to_centre` → **Decimal Number**
   - `year`, `stop_sequence`, `travel_min_to_centre` → **Whole Number**
   - everything else → **Text**
4. **Home → Close & Apply**. The data loads; you'll see the table fields on
   the right.

---

## 4. The one thing beginners get wrong: aggregation

The table has **many rows per station** (one per year × bedroom slice ×
property type). If you drop `avg_rent` straight onto a chart, Power BI
**sums** them and you get nonsense like €40,000 rent.

Fix it once by creating explicit **measures** (reusable calculations). In the
**Data** view (left toolbar, the grid icon), **Home → New measure**, and
paste each of these one at a time (press Enter after each):

```DAX
Avg Rent = AVERAGE(luas_rent_powerbi[avg_rent])
```

```DAX
Dublin Avg = AVERAGE(luas_rent_powerbi[dublin_avg])
```

```DAX
Vs Dublin % = DIVIDE([Avg Rent] - [Dublin Avg], [Dublin Avg])
```

```DAX
Cheapest Stop Rent = MIN(luas_rent_powerbi[avg_rent])
```

```DAX
Dearest Stop Rent = MAX(luas_rent_powerbi[avg_rent])
```

```DAX
City Centre Rent =
CALCULATE([Avg Rent], luas_rent_powerbi[stop_sequence] = 0)
```

These six measures drive every visual below. Using `[Avg Rent]` instead of
the raw column is what stops the summing problem.

---

## 5. Add the slicers (do this first — they control everything)

Go back to **Report** view (top icon on the left). For each slicer:
**Visualizations → Slicer** icon, then drag a field into it.

1. Slicer 1 → field **`year`**. In its format pane set it to a
   **dropdown** (or keep as a list). Click **2025** so the report opens on
   the latest year.
2. Slicer 2 → field **`bedrooms`**. Set to dropdown, select
   **`1 to 2 bed`**. *(This is the only slice published for every area —
   see the analysis. With "All bedrooms" the map/bars mislead.)*
3. Slicer 3 → field **`property_type`**, dropdown, select
   **`All property types`**.

Arrange the three slicers in a row across the top. Everything else on the
page will now respect these three filters.

---

## 6. KPI cards

Use the **Card** visual four times (Visualizations → Card):

| Card | Field to drop in | Rename the visual title to |
|------|------------------|----------------------------|
| 1 | measure **City Centre Rent** | "City-centre rent" |
| 2 | measure **Cheapest Stop Rent** | "Cheapest stop (€)" |
| 3 | measure **Dearest Stop Rent** | "Dearest stop (€)" |
| 4 | measure **Vs Dublin %** | "Avg vs Dublin county" |

For each: select the card → **Format (paint-roller) → Callout value →**
set Display units to None and decimals to 0. Format the three rent measures
as Currency (€) and `Vs Dublin %` as Percentage. Put the four cards in a row
under the slicers.

---

## 7. The map

1. **Visualizations → Map** (the globe — the "Azure Map" or basic "Map" is
   fine; if the map visual is greyed out, enable it in **File → Options →
   Preview / Security → uncheck "block map visuals"**, or use the **"Map"**
   under "Build a visual").
2. Drag **`latitude`** into the **Latitude** well, **`longitude`** into
   **Longitude**.
3. Drag measure **Avg Rent** into **Bubble size**, and **`station`** into
   **Legend** or **Location** so each stop is a separate bubble.
4. Optional: drag **Avg Rent** into the colour/saturation well so cheap
   stops are green, dear ones red (Format → Bubble colours → conditional).

If the basic Map needs internet/Bing and is awkward, the **"Filled map"**
or the **scatter-on-coordinates** trick also works — but the standard Map
visual with lat/long is the simplest.

---

## 8. Bar chart — rent per station

1. **Visualizations → Clustered bar chart** (horizontal bars read better
   with 24 station names).
2. **Y-axis:** `station`. **X-axis:** measure **Avg Rent**.
3. To keep the physical line order, open Data view, select the `station`
   column, then **Column tools → Sort by column → stop_sequence**. Return to
   Report view and sort the visual by station ascending.
4. Format → Data colors → conditional formatting on **Avg Rent** for a
   green-to-red scale.

---

## 9. Line chart — the line vs Dublin over time

This one **ignores the Year slicer on purpose** (it shows all years), so
we'll tell it to.

1. **Visualizations → Line chart**.
2. **X-axis:** `year`. **Y-axis:** add **both** measures **Avg Rent** and
   **Dublin Avg**.
3. Select the visual → **Format → Edit interactions** isn't needed; instead
   stop the Year slicer filtering it: with the line chart selected, go to
   **Format → Edit interactions** on the *Year slicer* and set the line
   chart to **None**. (Edit interactions is on the **Format** ribbon tab
   when a slicer is selected.)
4. Title it "Green Line vs Dublin county, 2008–2025".

---

## 10. Scatter — rent vs commute (the headline finding)

1. **Visualizations → Scatter chart**.
2. **X-axis:** `travel_min_to_centre`. **Y-axis:** measure **Avg Rent**.
3. **Values / Details:** `station` (so each stop is one dot).
4. Add a **trend line:** select the visual → **Analytics (the magnifying-
   glass icon) → Trend line → Add**. It'll be nearly flat — that's the
   point: commute time barely predicts rent on this line.
5. Title it "Rent vs commute time — almost no gradient".

---

## 11. Make it look like a dashboard

- **View → Themes → Browse for themes** → pick **`luas_theme.json`** (in
  this `powerbi/` folder). It sets the Luas-green palette, fonts and rounded
  card borders in one click — no manual formatting needed.
- Add a **Text box** at the top as a title: *"Luas Green Line — Rent
  Explorer"* and a one-line subtitle.
- Line everything up: slicers row, KPI cards row, then map + bar on one
  row, line + scatter on the next.
- Right-click each visual → check titles are readable; turn off chart
  gridlines you don't need.

---

## 12. Save and export screenshots

1. **File → Save as → `dashboard.pbix`**, save it into the repo's
   `powerbi/` folder.
2. Take screenshots for the README:
   - whole page → save as `powerbi/screenshots/dashboard_overview.png`
   - the map close-up → `powerbi/screenshots/map.png`
   - the scatter/gradient → `powerbi/screenshots/gradient.png`
   - (Windows: **Win + Shift + S** to snip.)
3. Move the `.pbix` and screenshots back to the Mac repo (USB, email,
   OneDrive, or commit them directly from the Windows clone).

---

## 13. Commit

From the Mac (or the Windows clone):

```bash
git add powerbi/
git commit -m "Add Power BI dashboard and screenshots"
git push
```

> `.pbix` files are binary and can be a few MB — that's fine to commit.
> The screenshots are what the README will actually display.

---

## If you get stuck

The two classic beginner errors:

1. **Rent shows as a huge number** → you dropped the raw `avg_rent` column
   instead of the **`Avg Rent` measure**. Use the measure.
2. **The map/bars look identical for every filter** → your slicers aren't
   set, so it's averaging across all years and bedroom types at once. Pick
   one value in each slicer (2025 / 1 to 2 bed / All property types).

Send me a screenshot of whatever you're seeing and I'll talk you through it.
