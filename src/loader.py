import os
import pandas as pd
from loguru import logger

def load_data(df, config):
    if df.empty:
        logger.info("No data to load.")
        return

    data_dir = config["paths"]["data_dir"]
    partition_cols = config["partitioning"]

    # Validate partition columns
    missing_cols = [col for col in partition_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Partition columns missing: {missing_cols}")

    os.makedirs(data_dir, exist_ok=True)

    # Group by year/month (or whatever config says)
    for keys, group in df.groupby(partition_cols):
        # keys is a tuple like (2019, 12)
        partition_path = data_dir

        # Build folder structure dynamically
        for col, value in zip(partition_cols, keys):
            partition_path = os.path.join(partition_path, f"{col}={value}")

        os.makedirs(partition_path, exist_ok=True)

        symbol = group["symbol"].iloc[0]
        year = group["year"].iloc[0]
        month = group["month"].iloc[0]

        file_name = f"{symbol}_{year}_{month}.parquet"
        file_path = os.path.join(partition_path, file_name)

        group.to_parquet(file_path, index=False, compression="snappy")
        logger.info(f"Parquet written: {file_path}")