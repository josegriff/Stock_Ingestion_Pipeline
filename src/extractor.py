"""
Extractor: Fetches incremental OHLCV data from Yahoo Finance.
"""

import yfinance as yf
import pandas as pd
import os
import json
from loguru import logger



BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_FILE = os.path.join(BASE_DIR, "state", "last_extracted.json")
os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)



def load_state():
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def fetch_incremental(symbol, config):
    logger.error(">>> ENTERED EXTRACTOR FUNCTION <<<")
    years_back = config["years_back"]
    logger.info(f"Fetching data for {symbol}")

    state = load_state()
    last_date = state.get(symbol)

    end_date = pd.Timestamp("2026-02-24")
    start_date = end_date - pd.DateOffset(years=years_back)

    # Fetch data
    logger.error(f"DEBUG SYMBOL RECEIVED: {repr(symbol)}")
    df = yf.Ticker(symbol).history(start=start_date, end=end_date)
    logger.error(f"DEBUG RAW DF EMPTY? {df.empty}")
    logger.error(f"DEBUG RAW DF SHAPE: {df.shape}")

    if df.empty:
        logger.warning(f"No data returned for {symbol}")
        return pd.DataFrame()

    df = df.reset_index()
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"])
    df = df.sort_values("Date")

    df["date_str"] = df["Date"].dt.strftime("%Y-%m-%d")

    # Incremental filtering
    if last_date:
        df = df[df["date_str"] > last_date]

    if df.empty:
        logger.info(f"No new data for {symbol}")
        return pd.DataFrame()

    # Update state
    state[symbol] = df["date_str"].max()
    save_state(state)

    logger.error(f"DEBUG SYMBOL RECEIVED: {repr(symbol)}")
    return df