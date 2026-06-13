"""Chart and map helpers. Static figures are saved to reports/figures/."""

from pathlib import Path

import folium
import branca.colormap as cm

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FIGURES_DIR = PROJECT_ROOT / "reports" / "figures"


def save_fig(fig, name):
    """Save a matplotlib figure to reports/figures/ and return the path."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    path = FIGURES_DIR / f"{name}.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    return path


def station_rent_map(stations_with_rent, rent_col="avg_rent"):
    """Folium map of the line, stations coloured by rent.

    Expects one row per station with latitude/longitude and a rent column.
    """
    df = stations_with_rent
    centre = [df["latitude"].mean(), df["longitude"].mean()]
    fmap = folium.Map(location=centre, zoom_start=12, tiles="cartodbpositron")

    colormap = cm.LinearColormap(
        ["green", "yellow", "red"],
        vmin=df[rent_col].min(), vmax=df[rent_col].max(),
        caption="Average monthly rent (EUR)",
    )
    colormap.add_to(fmap)

    # Draw the line itself first so markers sit on top
    path = df.sort_values("stop_sequence")[["latitude", "longitude"]].values.tolist()
    folium.PolyLine(path, color="#444", weight=3, opacity=0.6).add_to(fmap)

    for _, row in df.iterrows():
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=8,
            color=colormap(row[rent_col]),
            fill=True,
            fill_opacity=0.9,
            popup=folium.Popup(
                f"<b>{row['station']}</b><br>"
                f"€{row[rent_col]:,.0f}/month<br>"
                f"{row['travel_min_to_centre']} min to St. Stephen's Green",
                max_width=220,
            ),
        ).add_to(fmap)
    return fmap


def save_map(fmap, name):
    """Save a folium map to reports/figures/ as a standalone HTML file."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    path = FIGURES_DIR / f"{name}.html"
    fmap.save(str(path))
    return path
