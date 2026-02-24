"""
Purpose of transformer.py:
Transforms raw Yahoo Finance OHLCV DataFrame into a clean,
analytics-ready DataFrame with symbol, year, month, and date fields.
"""

import pandas as pd
from loguru import logger


def transform_data(df, symbol):
    """
    Takes a native Yahoo Finance DataFrame and enriches it with:
    - symbol
    - date (string)
    - year
    - month
    - day

    Returns a clean DataFrame ready for loading.
    """

    if df.empty:
        logger.warning(f"Transformer received empty DataFrame for {symbol}")
        return pd.DataFrame()

    # Ensure Date column exists
    if "Date" not in df.columns:
        logger.error(f"Missing 'Date' column in DataFrame for {symbol}. Columns: {df.columns}")
        return pd.DataFrame()

    # Convert Date to datetime if needed
    if not pd.api.types.is_datetime64_any_dtype(df["Date"]):
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    df = df.dropna(subset=["Date"])  # remove invalid dates

    # Add symbol column
    df["symbol"] = symbol

    # Add date parts
    df["year"] = df["Date"].dt.year
    df["month"] = df["Date"].dt.month
    df["day"] = df["Date"].dt.day

    # Convert Date to string for partitioning
    df["date_str"] = df["Date"].dt.strftime("%Y-%m-%d")

    # Reorder columns (optional but clean)
    ordered_cols = [
        "symbol", "Date", "date_str",
        "Open", "High", "Low", "Close", "Volume",
        "year", "month", "day"
    ]

    df = df[ordered_cols]

    logger.info(f"Transformed DataFrame for {symbol}: {len(df)} rows")

    return df