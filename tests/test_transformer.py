import pandas as pd
from src.transformer import transform_data

def test_transform_data_basic():        # Fake Alpha Vantage time series
    fake_time_series = {
        "2024-06-14": {
            "1. open": "100.0",
            "2. high": "110.0",
            "3. low": "90.0",
            "4. close": "105.0",
            "5. volume": "1500000"
        },
        "2024-06-13": {
            "1. open": "102.0",
            "2. high": "112.0",
            "3. low": "92.0",
            "4. close": "107.0",
            "5. volume": "1300000"
        }
    }
    
    df = transform_data("BP.L",  fake_time_series)
    
#   Structure checks
    assert df is not None
    assert isinstance (df, pd.DataFrame)
    assert len(df) == 2
    
#   Column checks
    expected_cols = {
        "date", "open", "high", "low", "close", 
        "volume", "symbol", "ingested_at"
    }
    assert expected_cols.issubset(set(df.columns))

#   Date columns is datetime
    assert pd.api.types.is_datetime64_any_dtype(df["date"])
    
#   Numeric type checks
    assert pd.api.types.is_float_dtype (df["open"])
    assert pd.api.types.is_float_dtype (df["high"])
    assert pd.api.types.is_float_dtype (df["low"])
    assert pd.api.types.is_float_dtype (df["close"])
    assert pd.api.types.is_integer_dtype (df["volume"])
    
#   Ingested_at exists and is datetime
    assert pd.api.types.is_datetime64_any_dtype (df["ingested_at"])
    