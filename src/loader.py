"""
    Purpose of loader.py:
    Load saves to parquet and enables DuckDB queries. 
    Parquet is used because it is fast, compressed, and 
    partitioned for efficient querying.
    DuckDB is used for simple, fast SQL analytics.
"""

import pyarrow as pa
import pyarrow.parquet as pq
import duckdb
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

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
        Exmaple: 
            "SELECT * FROM stock_data WHERE symbol='BP.L'"
    """
    
    con = duckdb.connect()                           # In-memory DuckDB
    con.execute(f"""
            CREATE VIEW stock_data AS
            SELECT * FROM parquet_scan('{DATA_DIR}/**/*.parquet');
            """)                                     # Scans all parquet files recursively

    return con.execute(sql_query).fetchdf()              # Runs SQL, returns DataFrame  
