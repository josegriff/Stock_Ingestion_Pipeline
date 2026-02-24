"""
Purpose of orchestrator.py:
Coordinates the ETL pipeline:
- Loads config
- Loops through symbols
- Extracts incremental data (DataFrame)
- Transforms it (DataFrame)
- Loads it into partitioned Parquet
"""

import yaml
from loguru import logger

from .extractor import fetch_incremental
from .transformer import transform_data
from .loader import load_data


def run_pipeline():
    # Load config.yaml
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)

    symbols = config["symbols"]

    for symbol in symbols:
        logger.info(f"--- Processing {symbol} ---")

        try:
            # Extract (returns DataFrame)
            raw_df = fetch_incremental(symbol, config)

            # FIX: DataFrame truth-value ambiguity → use .empty
            if raw_df.empty:
                logger.info(f"No new data for {symbol}, skipping.")
                continue

            # Transform (returns DataFrame)
            df = transform_data(raw_df, symbol)

            if df.empty:
                logger.info(f"Transformed DataFrame empty for {symbol}, skipping.")
                continue

            # Load
            load_data(df, config)

        except Exception as e:
            logger.error(f"Error processing {symbol}: {e}")

    logger.info("Pipeline completed successfully.")