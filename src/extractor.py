"""
    Purpose of extractor.py:
    Extraction pulls data from Yahoo Finance (no API key needed).
"""

import yfinance as yf
from loguru import logger
import os
import json
from datetime import datetime

# Base directory for state file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_FILE = os.path.join(BASE_DIR, "state", "last_extracted.json")

# Ensure state directory exists
os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)


def load_state():
    """Loads last fetched dates from JSON file."""
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_state(state):
    """Saves updated state to JSON file."""
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def fetch_incremental(symbol):
    """
    Fetches only new stock data since last fetch using Yahoo Finance.
    Updates state with latest date.
    """

    logger.info(f"Fetching data for symbol: {symbol}")

    state = load_state()
    last_date = state.get(symbol)  # e.g. '2026-02-15'

    # Fetch full history (Yahoo handles caching internally)
    ticker = yf.Ticker(symbol)
    df = ticker.history(period="5y")  # full history

    if df.empty:
        logger.warning(f"No data returned for {symbol}")
        return {}

    # Reset index to get date column
    df = df.reset_index()

    # Convert date to string for comparison
    df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")

    # Filter incremental data
    if last_date:
        df = df[df["Date"] > last_date]

    if df.empty:
        logger.info(f"No new data for {symbol}")
        return {}

    # Update state with latest date
    new_last = df["Date"].max()
    state[symbol] = new_last
    save_state(state)

    # Convert to dict format similar to Alpha Vantage output
    time_series = {}
    for _, row in df.iterrows():
        time_series[row["Date"]] = {
            "1. open": row["Open"],
            "2. high": row["High"],
            "3. low": row["Low"],
            "4. close": row["Close"],
            "5. volume": row["Volume"],
        }

    return time_series