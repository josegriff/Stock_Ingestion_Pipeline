"""
    Purpose of loader.py:
    Load saves to parquet and enables DuckDB queries. 
    Parquet used because it is fast, compressed, and 
    partitioned (by symbol/date) for quick access without 
    loading all data
    DuckDB used over full DB for simplicity and speed.
"""

import pyarrow as pa
import pyarrow.parquet as pq
import duckdb
import os

DATA_DIR = "../data/"                                 # Relative path from src

def load_to_parquet(df):
    """
        Appends Dataframe to partitioned parquet dataset.
        Partitions by symbol and date for efficient queries.
    """
    
    if df is None:
        return
    os.makedirs(DATA_DIR, exist_ok=True)              # Create data dir if missing
    table = pa.table.from_pandas(df)                  # Convert DataFrame to Arrow Table
    pq.write_to_dataset(                              # Appends without duplicates. Folders auto-created
        table,
        root_path=DATA_DIR,
        partition_cols=["symbol", "date"]             # Creates folders like symbol=AAPL/date=2026-02-15
    )
    
def query_data(sql_query):
    """
        Queries the parquet dataset using DuckDB SQL.
        Exmaple: "SELECT * FROM stock_data WHERE symbol='BP.L'"
    """
    
    con = duckdb.connect()                          # In-memory DuckDB
    con.register("stock_data", pq.read_table(DATA_DIR))
#   ^^^Register entire dataset as a virtual table^^^

    return con.execute(query).fetchdf()             # Runs SQL, returns DataFrame  
