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
from loguru import logger

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

def load_to_parquet(df):
    """
        Appends Dataframe to partitioned parquet dataset.
        Partitions by symbol and date for efficient queries.
    """
    
    if df is None or df.empty:
        logger.warning("No new data to write - skipping Parquet load.")
        return
    
    os.makedirs(DATA_DIR, exist_ok=True)              # Create data dir if missing
    
    try:
        table = pa.Table.from_pandas(df)                  # Convert DataFrame to Arrow Table
    except Exception as e:
        logger.error(f"Failed converting DatafFrame to Arrow Table: {e}")
        raise
    try:
        pq.write_to_dataset(                              # Appends without duplicates. Folders auto-created
            table,
            root_path=DATA_DIR,
            partition_cols=["symbol", "year", "month"]             # Creates folders like symbol=AAPL/year=2026/month=02
        )
        logger.info(f"Parquet written for {df['symbol'].iloc[0]} with {len(df)} rows.")
    except Exception as e:
        logger.error(f"Failed writing Parquet dataset: {e}")
        raise
    
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
