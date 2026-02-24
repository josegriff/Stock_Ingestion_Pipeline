import pandas as pd

def transform_data(symbol, time_series):
    """
    Converts Yahoo dict into a DataFrame.
    """

    if not time_series:
        return pd.DataFrame()   # Always return a DataFrame

    df = pd.DataFrame.from_dict(time_series, orient='index')

    df.index.name = "date"
    df.reset_index(inplace=True)

    df.rename(columns={
        '1. open': 'open',
        '2. high': 'high',
        '3. low': 'low',
        '4. close': 'close',
        '5. volume': 'volume',
    }, inplace=True)

    df["date"] = pd.to_datetime(df["date"])   

    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month

    df = df.astype({
        'open': float,
        'high': float,
        'low': float,
        'close': float,
        'volume': int,
    })

    df["symbol"] = symbol
    df["ingested_at"] = pd.Timestamp.utcnow()

    return df