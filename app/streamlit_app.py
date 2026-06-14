"""Luas Green Line rent explorer - Streamlit dashboard.

Run locally:
    streamlit run app/streamlit_app.py

Deployed on Streamlit Community Cloud. The SQLite database is not committed
to git, so on a fresh clone (which is what the Cloud runs) it is rebuilt
from the CSVs the first time the app starts - see ensure_database().
"""

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from streamlit_folium import st_folium

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))

from sql_utils import DB_PATH, build_database, run_sql  # noqa: E402
from analysis import fit_gradient  # noqa: E402
from visualize import station_rent_map  # noqa: E402

st.set_page_config(page_title="Luas Green Line Rent Explorer",
                   page_icon="🚊", layout="wide")


# --------------------------------------------------------------------------- #
# Data access (cached so the queries only run once per filter combination)
# --------------------------------------------------------------------------- #
@st.cache_resource
def ensure_database():
    """Build the SQLite db on first run if it isn't there (e.g. on Cloud)."""
    if not DB_PATH.exists():
        build_database()
    return True


@st.cache_data
def load_stations():
    return pd.read_csv(ROOT / "data" / "luas_stations.csv")


@st.cache_data
def station_rents(year, bedrooms, property_type):
    """Rent per station for one slice, with coordinates merged in.

    The station_rents view holds the rent; latitude/longitude live only in
    the stations table, so they are merged on afterwards.
    """
    rent = run_sql(f"""
        SELECT stop_sequence, station, travel_min_to_centre,
               distance_km_to_centre, avg_rent
        FROM station_rents
        WHERE year = {year}
          AND bedrooms = '{bedrooms}'
          AND property_type = '{property_type}'
        ORDER BY stop_sequence
    """)
    coords = load_stations()[["station", "latitude", "longitude"]]
    return rent.merge(coords, on="station", how="left")


@st.cache_data
def line_trend(bedrooms, property_type):
    return run_sql(f"""
        SELECT year, ROUND(AVG(avg_rent)) AS line_avg
        FROM station_rents
        WHERE bedrooms = '{bedrooms}'
          AND property_type = '{property_type}'
        GROUP BY year
        ORDER BY year
    """)


@st.cache_data
def dublin_trend(bedrooms, property_type):
    return run_sql(f"""
        SELECT year, avg_rent AS dublin_avg
        FROM rents
        WHERE location = 'Dublin'
          AND bedrooms = '{bedrooms}'
          AND property_type = '{property_type}'
        ORDER BY year
    """)


@st.cache_data
def available_options():
    years = run_sql("SELECT DISTINCT year FROM rents ORDER BY year DESC")["year"].tolist()
    beds = run_sql("SELECT DISTINCT bedrooms FROM rents ORDER BY bedrooms")["bedrooms"].tolist()
    props = run_sql("SELECT DISTINCT property_type FROM rents ORDER BY property_type")["property_type"].tolist()
    return years, beds, props


# --------------------------------------------------------------------------- #
# Layout
# --------------------------------------------------------------------------- #
ensure_database()
stations = load_stations()
years, bedroom_opts, property_opts = available_options()

st.title("🚊 Luas Green Line Rent Explorer")
st.markdown(
    "How does rent change as you ride the Green Line out of Dublin city "
    "centre? Pick a year and property type on the left and explore. Rent "
    "figures are the RTB's average registered tenancy rents; each station "
    "inherits the figure for its surrounding RTB area."
)

with st.sidebar:
    st.header("Filters")
    year = st.select_slider("Year", options=sorted(years), value=max(years))

    # Default to the only slice published for every area on the line.
    default_bed = bedroom_opts.index("1 to 2 bed") if "1 to 2 bed" in bedroom_opts else 0
    bedrooms = st.selectbox("Bedrooms", bedroom_opts, index=default_bed)
    st.caption("'1 to 2 bed' is the only slice the RTB publishes for every "
               "area on the line - other slices have gaps.")

    property_type = st.selectbox("Property type", property_opts, index=0)

data = station_rents(year, bedrooms, property_type)

if data.empty or data["avg_rent"].isna().all():
    st.warning(
        f"The RTB doesn't publish a **{bedrooms} / {property_type}** figure "
        f"for these areas in {year}. Try '1 to 2 bed' and 'All property types'."
    )
    st.stop()

data = data.dropna(subset=["avg_rent"])

# --------------------------------------------------------------------------- KPIs
centre = data[data["stop_sequence"] == 0]
centre_rent = centre["avg_rent"].iloc[0] if not centre.empty else data["avg_rent"].iloc[0]
cheapest = data.loc[data["avg_rent"].idxmin()]
dearest = data.loc[data["avg_rent"].idxmax()]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Stations with data", f"{len(data)} / 24")
c2.metric("City-centre rent", f"€{centre_rent:,.0f}")
c3.metric("Cheapest stop", f"€{cheapest['avg_rent']:,.0f}", cheapest["station"],
          delta_color="off")
c4.metric("Dearest stop", f"€{dearest['avg_rent']:,.0f}", dearest["station"],
          delta_color="off")

tab_map, tab_line, tab_trend, tab_value = st.tabs(
    ["🗺️ Map", "📊 Rent along the line", "📈 Trend since 2008", "💶 Value for money"]
)

# --------------------------------------------------------------------------- Map
with tab_map:
    st.subheader(f"Rent by station, {year}")
    st.caption("Green = cheaper, red = dearer. Click a marker for detail.")
    fmap = station_rent_map(data)
    st_folium(fmap, height=520, use_container_width=True, returned_objects=[])

# --------------------------------------------------------------------- Bar chart
with tab_line:
    st.subheader(f"Average rent at each stop, {year}")
    fig = px.bar(
        data, x="station", y="avg_rent",
        color="avg_rent", color_continuous_scale="RdYlGn_r",
        labels={"avg_rent": "Avg rent (€)", "station": ""},
    )
    fig.update_layout(coloraxis_showscale=False, xaxis_tickangle=-60, height=520)
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        "Tip: with 'All bedrooms' selected the line looks oddly flat - that's "
        "a housing-mix effect (big suburban houses vs small city apartments). "
        "Switch to '1 to 2 bed' for a like-for-like comparison."
    )

# ------------------------------------------------------------------- Trend chart
with tab_trend:
    st.subheader("The line vs Dublin county, 2008–2025")
    lt = line_trend(bedrooms, property_type)
    dt = dublin_trend(bedrooms, property_type)
    merged = lt.merge(dt, on="year", how="left")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=merged["year"], y=merged["line_avg"],
                             mode="lines+markers", name="Green Line (avg stop)"))
    fig.add_trace(go.Scatter(x=merged["year"], y=merged["dublin_avg"],
                             mode="lines+markers", name="Dublin county"))
    fig.add_vline(x=year, line_dash="dot", line_color="grey")
    fig.update_layout(height=480, yaxis_title="Avg rent (€)", xaxis_title="Year",
                      legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"Dotted line marks {year}, the year selected on the left.")

# ------------------------------------------------------------------- Value chart
with tab_value:
    st.subheader(f"Rent vs commute time, {year}")
    commute = data[data["travel_min_to_centre"] > 0].copy()

    if len(commute) >= 2:
        slope, intercept, r2 = fit_gradient(commute)
        fig = px.scatter(
            commute, x="travel_min_to_centre", y="avg_rent",
            hover_name="station",
            labels={"travel_min_to_centre": "Commute to city centre (min)",
                    "avg_rent": "Avg rent (€)"},
        )
        xs = [0, commute["travel_min_to_centre"].max()]
        fig.add_trace(go.Scatter(
            x=xs, y=[intercept + slope * x for x in xs],
            mode="lines", name="Best fit",
            line=dict(color="crimson", dash="dash"),
        ))
        fig.update_layout(height=480, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

        col1, col2 = st.columns(2)
        col1.metric("€ saved per extra commute minute", f"{-slope:,.1f}")
        col2.metric("R² (how well commute explains rent)", f"{r2:.2f}")
        if r2 < 0.1:
            st.info(
                "The R² is tiny: on the Green Line, commute time barely "
                "explains rent at all. Rent here is set by the *area*, not "
                "by distance from town - the corridor is uniformly affluent "
                "from end to end. This holds in every year since 2008."
            )
    else:
        st.warning("Not enough stations with data for this slice to fit a line.")

st.divider()
st.caption(
    "Data: RTB Average Monthly Rent Report (CSO table RIA02) · "
    "Luas stop locations from Transport Infrastructure Ireland · "
    "Built with Streamlit, Plotly and Folium."
)
