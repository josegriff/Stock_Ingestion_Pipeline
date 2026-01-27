"""
    Purpose of transformer.py: 
    Transform raw JSON into a structured DateFrame. 
    This makes it easier to analyse and visualise the stock data.
"""

import pandas as pd
from datetime import datetime

def transform_data(symbol, time_series):
    """
    Converts Alpha Vantage time series dict into a DataFrame.
    Adds symbol and ingestion timestamp
    Ensures correct data types
    """

    if not time_series: 
        return None                             # No new data to process
    
    df = pd.DataFrame.from_dict(time_series, orient='index')
    #        ^^^ Builds table from dict ^^^
    
    df.index.name = "date"                      # Name index for clarity, dates as rows
    df.reset_index(inplace=True)                # Moves date to column for partitioning later

    df.rename(columns={                         # Renames Alpha Vantage columns to simpler names
        '1. open': 'open',
        '2. high': 'high',
        '3. low': 'low',
        '4. close': 'close',
        '5. volume': 'volume',
    }, inplace=True)
    
    df["date"] = pd.to_datetime(df["date"])     # Convert date column to datetime
    df = df.astype({                            # Convert numeric columns to correct types
        'open': float,
        'high': float,
        'low': float,
        'close': float,
        'volume': int,
    })

    df["symbol"] = symbol                       # Add symbol column
    df["ingested_at"] = pd.Timestamp.utcnow()   # Add ingestion timestamp
    return df
    
    