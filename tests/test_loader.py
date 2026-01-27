import pandas as pd
import os
import duckdb
import pyarrow.parquet as pq

from src.loader import load_to_parquet, query_data

def test_load_to_parquet(tmp_path, monkeypatch):
#   Redirect DATA_DIR to temporary directory for testing
    
    monkeypatch.setattr(
        "src.loader.DATA_DIR", (tmp_path)
    )
    
    df = pd.DataFrame({                                 # Create a sample DataFrame
        "date": pd.to_datetime(["2024-06-14", "2024-06-13"]),
        "open": [100.0, 102.0],
        "high": [110.0, 112.0],
        "low": [90.0, 92.0],
        "close": [105.0, 107.0],
        "volume": [1500000, 1300000],
        "symbol": ["BP.L", "BP.L"],
        "ingested_at": pd.Timestamp.utcnow()
    })
    
    load_to_parquet(df)                                 # Write to parquet
    
#   Assert parquet files were created in partitioned folders
    symbol_folder = tmp_path / "symbol=BP.L"
    assert symbol_folder.exists()
    
    date_folders = list(symbol_folder.glob("date=*"))   # There should be a date partition folder inside
    assert len(date_folders) == 2                       # One per row

def test_query_data(tmp_path, monkeypatch):
    monkeypatch.setattr(                                #Redirect DATA_DIR to temporary directory
        "src.loader.DATA_DIR", (tmp_path)
    )    
    
    df = pd.DataFrame({                                 # Create a sample DataFrame
        "date": pd.to_datetime(["2024-06-14"]),
        "open": [100.0],
        "high": [110.0],
        "low": [90.0],
        "close": [105.0],
        "volume": [1500000],
        "symbol": ["BP.L"],
        "ingested_at": pd.Timestamp.utcnow()
    })
    
    load_to_parquet(df)                                 # Write to parquet
    
    result = query_data
    ("SELECT * FROM stock_data WHERE symbol='BP.L'")    # Query using DuckDB
    
#   Assert the query returns the expected data
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 1
    assert result.iloc[0]["symbol"] == 100.0          
        
