"""
    Purpose of transformer.py: 
    Transform turns raw JSON into a structured DateFrame. 
    This makes it easier to analyse and visualise the stock data.
"""

import pandas as pd
from datetime import datetime

def transform_data(symbol, time_series):
    """
    Converts time series dict to DataFrame.
    Adds symbol and ingestion timestamp
    Types columns for efficiency.
    """
    
    if not time_series: 
        return None                             # No new data to process
    df = pd.DataFrame.from_dict(time_series, orient='index')
    #        ^^^ Builds table from dict ^^^
    
    df.index.name = "date"                      # Name index for clarity, dates as rows
    df.reset_index(inplace=True)                # Moves date to column for partitioning later
    df["symbol"] = symbol                       # Add symbol to each row
    df["ingested_at"] = ["date", "open", "high", "low", "close", 
                         "volume", "symbol", "ingested_at"]
    #       ^^^ Rename columns to clean names ^^^
    
    df = df.astype({                            #Ensures correct data types (memory efficiency)
        'open': float,
        'high': float,
        'low': float,
        'close': float,
        'volume': int,
    })
    df["date"] = pd.to_dateto,e(df["date"])     # Date string to datetime object
    return df
    
    