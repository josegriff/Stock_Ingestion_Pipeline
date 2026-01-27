"""
    Purpose of extractor.py:
    Extraction pulls data from API. 
"""

import requests
from tenacity import retry, stop_after_attempt, wait_exponential
from loguru import logger
import os
from dotenv import load_dotenv
import time                                             # For rate limit sleep

load_dotenv()                                           # Loads variables from .env file
API_KEY = os.getenv("API_KEY")
BASE_URL = "https://www.alphavantage.co/query"

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
#       Decorator from tenacity. Tries function 3 times, 
#       waiting longer each time on errors like network issues. 
#       Retries make it robust.

def fetch_stock_data(symbol):
    """
        Fetches daily stock data for a given symbol through 
        the Alpha Vantage API.
    """
    
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "outputsize": "compact",                        # Last 100 days for efficiency
        "apikey": API_KEY
    }
    response = requests.get(BASE_URL, params=params)    #Send GET request
    response.raise_for_status()                         # checks for errors
    return response.json()                              # Return dict from JSON


#   This is called in a loop later, with time.sleep(12) between calls for rate limits


#   Adding Incremental logic to avoid reduntant data fetching

import json 
from datetime import datetime

STATE_FILE = "../state/last_extracted.json"             # Relative path from src

def load_state():
    """ Loads last fetched dates from JSON file. """
    
    try:
        with open (STATE_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return{}                                        # Empty if first run
    
def save_state(state):
    """ Saves updated state to JSON file. """
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)
        
def fetch_incremental(symbol):
    """
        Fetches only new stock data since last fetch
        Updates state with latest date
    """
    state = load_state()
    last_date = state.get(symbol)                       # e.g. '2026-02-15'
    data = fetch_stock_data(symbol)
    time_series = data.get("Time Series (Daily)", {})
    if last_date:
        time_series = {d: v for d, v in time_series.items() if d > last_date} 
#                          ^^^Filters new data^^^        
    if time_series:
        new_last = max(time_series.keys())              # Fetches latest date
        state[symbol] = new_last
        save_state(state)
    return time_series                                  # Dict of new dates to OHLCV data

            
    