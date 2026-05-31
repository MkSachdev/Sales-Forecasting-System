from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
HISTORICAL_DATA_PATH = PROJECT_ROOT / "data" / "Forecasting Case-Sheet1.csv"
FORECAST_DATA_PATH = PROJECT_ROOT / "data" / "all_state_forecasts.csv"


def _clean_sales_amount(series: pd.Series) -> pd.Series:
    return pd.to_numeric(
        series.astype(str).str.replace(",", "", regex=False).str.strip(),
        errors="coerce",
    )


def load_historical_sales() -> pd.DataFrame:
    """Load historical sales data for dashboard visualization."""
    df = pd.read_csv(HISTORICAL_DATA_PATH)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Sales"] = _clean_sales_amount(df["Total"])
    df = df.dropna(subset=["State", "Date", "Sales"])
    return df.sort_values(["State", "Date"]).reset_index(drop=True)


def load_forecast_sales() -> pd.DataFrame:
    """Load the existing 8-week forecast output without recalculating it."""
    df = pd.read_csv(FORECAST_DATA_PATH)
    df["Forecasted_Sales"] = pd.to_numeric(df["Forecasted_Sales"], errors="coerce")
    df["Week_Number"] = (
        df["Week"].astype(str).str.extract(r"(\d+)").astype(float).astype("Int64")
    )
    df = df.dropna(subset=["State", "Week", "Forecasted_Sales", "Week_Number"])
    return df.sort_values(["State", "Week_Number"]).reset_index(drop=True)


def weekly_sales_for_state(historical_df: pd.DataFrame, state: str) -> pd.DataFrame:
    state_df = historical_df[historical_df["State"] == state].copy()
    return (
        state_df.set_index("Date")
        .resample("W")["Sales"]
        .sum()
        .reset_index()
        .sort_values("Date")
    )
