"""Statistical helpers shared by the notebooks and the Streamlit app."""

import pandas as pd
from sklearn.linear_model import LinearRegression


def fit_gradient(df, x_col="travel_min_to_centre", y_col="avg_rent"):
    """Fit rent = intercept + slope * commute_minutes.

    Returns (slope, intercept, r_squared). Slope is 'euro per extra minute
    of commute' - negative means rent falls as you move out.
    """
    X = df[[x_col]].to_numpy()
    y = df[y_col].to_numpy()
    model = LinearRegression().fit(X, y)
    return float(model.coef_[0]), float(model.intercept_), float(model.score(X, y))


def gradient_by_year(station_rents, bedrooms="1 to 2 bed",
                     property_type="All property types"):
    """Refit the rent-vs-commute line for every year separately.

    Shows how the 'distance discount' has changed over time.
    """
    subset = station_rents[
        (station_rents["bedrooms"] == bedrooms)
        & (station_rents["property_type"] == property_type)
    ]
    rows = []
    for year, grp in subset.groupby("year"):
        slope, intercept, r2 = fit_gradient(grp)
        rows.append({
            "year": year,
            "eur_per_minute": slope,
            "implied_centre_rent": intercept,
            "r_squared": r2,
            "stations": len(grp),
        })
    return pd.DataFrame(rows)


# Scheduled time between consecutive stops averages ~1.8 minutes, so the
# per-minute slope converts to a per-stop figure with this constant.
MINUTES_PER_STOP = 42 / 23  # end-to-end time / number of hops


def eur_per_stop(eur_per_minute):
    """Convert a per-minute gradient into 'euro per extra stop'."""
    return eur_per_minute * MINUTES_PER_STOP
