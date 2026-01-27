"""
    Purpose of orchestrator.py:
    Orchestrator manages the ETL workflow:
    1. Extracts data using extractor.py
    2. Transforms data using transformer.py
    3. Loads data using loader.py
"""

import yaml
from apscheduler.schedulers.blocking import BlockingScheduler
from loguru import logger
import time
import os

from .extractor import fetch_incremental
from .transformer import transform_data
from .loader import load_to_parquet

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "config", "watchlist.yaml")
LOG_PATH = os.path.join(BASE_DIR, "logs", "pipeline.log")

os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True) # Ensure log directory exists

logger.add(LOG_PATH, rotation="500 MB")               # Logs to file, rotates at 500MB

def run_pipeline():
    """ Runs ETL for all symbols in config"""
    
    with open("../config/symbols.yaml", "r") as f:    # Load watchlist
        config = yaml.safe_load(f)                    # Parses YAML safely
        symbols = config["symbols"]
        
    for symbol in symbols:                            # Process each symbol
        try:
            time_series = fetch_incremental(symbol)
            df = transform_data(symbol, time_series)
            load_to_parquet(df)
            
            if df is not None:
                logger.info(f"Successfully loaded new data for {symbol}")
            time.sleep(12)                            # 5 calls per minute rate limit (60/5=12s)
        
        except Exception as e:
            logger.error(f"Error processing {symbol}: {e}")
            
if __name__ == "__main__":                            # Runs only if file directly executed
    scheduler = BlockingScheduler()
    scheduler.add_job(run_pipeline, 'cron', hour=18)  # Runs daily at 6 PM (after market close)
    
    logger.info("Starting scheduler...")
    scheduler.start()
    