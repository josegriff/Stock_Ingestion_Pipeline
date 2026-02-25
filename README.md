# Stock Ingestion Pipeline with DuckDB Analytics
This project implements a production‑style stock ingestion pipeline that fetches OHLCV data from Yahoo Finance, stores it in a partitioned Parquet data lake, and exposes the data through a DuckDB analytics layer. The pipeline is incremental, config‑driven, and designed to be simple to run and easy to extend.

## Overview
The system ingests daily stock price data for a configurable watchlist of symbols. Data is extracted incrementally, transformed into a clean analytics‑ready schema, and written to a partitioned Parquet structure. DuckDB is used to query the lake directly, enabling efficient SQL analytics without a separate database server.
The project includes:
- A full ETL pipeline (extract → transform → load)
- A partitioned Parquet data lake
- A DuckDB view for analytics
- A SQL analytics layer
- A reporting script that executes all analytics queries
- A lightweight exploration script for sanity checks

## Tech Stack
### Languages and Tools
- Python
- DuckDB
- SQL
- YAML configuration
- Loguru for structured logging

### Data Source
- Yahoo Finance API (via `yfinance`)

### Storage
- Partitioned Parquet data lake
- Snappy compression

### Analytics
- DuckDB view (`stock_data`) created dynamically over the Parquet lake
- SQL analytics defined in `queries.sql`
- Python reporting engine (`report.py`)
- Sanity‑check explorer (`explore.py`)

## Architecture
```
Yahoo Finance API
        ↓
Extractor (incremental fetch)
        ↓
Transformer (schema + partition fields)
        ↓
Loader (partitioned Parquet)
        ↓
Data Lake (data/)
        ↓
DuckDB View (stock_data)
        ↓
SQL Analytics (queries.sql)
        ↓
Python Reporting (report.py)
```

## Features
### Ingestion
- Incremental extraction using a persistent state file
- Config‑driven watchlist and pipeline settings
- Clean transformation with enforced schema
- Partitioned Parquet output (`symbol/year/month`)
- Snappy compression for efficient storage
 
### Analytics
- DuckDB view over the Parquet lake
- SQL queries for returns, volatility, Sharpe ratio, drawdowns, correlations, momentum, and seasonality
- Reporting script with execution‑time measurement
- Exploration script for row counts, samples, and data validation

## Project Structure
```
src/
    extractor.py
    transformer.py
    loader.py
    orchestrator.py
main.py

config/
    config.yaml
    watchlist.yaml

analytics/
    queries.sql
    report.py
    explore.py
    analytics.duckdb

data/
    symbol=.../year=.../month=.../*.parquet

state/
    last_extracted.json

logs/
    pipeline.log
```


## How to Run the Pipeline
### 1. Run the ingestion pipeline
This fetches new data, transforms it, and writes Parquet files.
```
python main.py
```

### 2. Explore the data lake
This performs basic sanity checks.
```
python analytics/explore.py
```

### 3. Run the analytics report
This executes all SQL queries and prints formatted results.
```
python analytics/report.py
```


## Configuration
`config.yaml`
Controls ingestion settings:
- years_back
- data and state directories
- partitioning scheme
`watchlist.yaml`
Defines the list of symbols to ingest.

## Example Outputs
### Sample sanity check
```
=== TOTAL ROW COUNT ===
(7530,)

=== ROWS PER SYMBOL ===
  symbol   rows
0   AAPL   1255
1   AMZN   1255
...
```

### Sample analytics output
```
--- Query 4. Maximum drawdown per symbol ---
  symbol  max_drawdown
0   TSLA     -0.736322
1   NVDA     -0.663351
...
Execution time: 0.042 seconds
```


## What This Project Demonstrates
- Building a modular ETL pipeline in Python
- Managing incremental ingestion with state tracking
- Designing a partitioned Parquet data lake
- Using DuckDB as an embedded analytics engine
- Writing SQL analytics for financial time‑series
- Producing structured, repeatable reports

## Future Improvements
- Add unit tests for each pipeline stage
- Add a scheduler (cron, Airflow, or Prefect)
- Add data quality checks (missing days, anomalies)
- Add a Streamlit dashboard for interactive exploration
- Add forecasting or factor‑model analytics
