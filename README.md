# Stock Ingestion Pipeline  
A production‑ready ETL pipeline for ingesting, transforming, and storing daily stock market data using Alpha Vantage, PyArrow, Parquet, and DuckDB.

This project demonstrates a clean, modular, testable data‑engineering workflow with proper orchestration, partitioned storage, and automated scheduling.


---

## Features

### **Incremental Extraction**
- Pulls daily stock price data from Alpha Vantage  
- Automatically fetches only *new* dates  
- Handles API rate limits safely  

### **Robust Transformation Layer**
- Cleans and normalises Alpha Vantage JSON  
- Converts OHLC values to numeric types  
- Parses dates into proper datetime objects  
- Adds metadata: `symbol` and `ingested_at`  

### **Efficient Parquet Storage**
- Writes data to a **partitioned Parquet dataset**  
- Partitioned by:
  - `symbol`
  - `date`
- Enables fast analytical queries  

### **DuckDB Query Engine**
- Query all Parquet files using SQL  
- Supports partition pruning  
- Zero‑copy reads for high performance  

### **Orchestration**
- Runs the full ETL pipeline for all symbols in `watchlist.yaml`  
- Logs successes and failures  
- Optional daily scheduler (via APScheduler)  

### **Full Test Suite**
Includes unit tests for:
- Extractor  
- Transformer  
- Loader  
- Orchestrator (with mocks)  

---

## Project Structure

```
stock_ingestion_pipeline/
│
├── config/
│   ├── watchlist.yaml        # List of stock symbols
│   └── .env                  # API key (not committed)
│
├── data/                     # Parquet output (auto‑generated)
│
├── logs/
│   └── pipeline.log          # Log output
│
├── src/
│   ├── extractor.py          # Fetches incremental stock data
│   ├── transformer.py        # Cleans and normalises data
│   ├── loader.py             # Writes Parquet + DuckDB queries
│   └── orchestrator.py       # Runs the ETL workflow
│
├── tests/
│   ├── test_extractor.py
│   ├── test_transformer.py
│   ├── test_loader.py
│   └── test_orchestrator.py
│
└── main.py                   # Entry point for running the pipeline
```

---

## How It Works

The pipeline follows a clean ETL structure:

### **1. Extraction**
`fetch_incremental(symbol)`  
- Loads existing Parquet data (if any)  
- Determines the latest stored date  
- Calls Alpha Vantage  
- Fetches only *new* rows  

### **2. Transformation**
`transform_data(symbol, time_series)`  
- Converts JSON to a DataFrame  
- Renames OHLC columns  
- Casts numeric types  
- Parses dates  
- Adds metadata (`symbol`, `ingested_at`)  

### **3. Loading**
`load_to_parquet(df)`  
- Writes data to a **partitioned Parquet dataset**  
- Partitions by `symbol` and `date`  
- Ensures efficient storage and querying  

### **4. Querying**
`query_data(sql)`  
- Uses DuckDB’s `parquet_scan`  
- Enables fast SQL analytics directly on Parquet  

### **5. Orchestration**
`run_pipeline()`  
- Loads symbols from `watchlist.yaml`  
- Runs extract → transform → load for each  
- Logs successes and failures  
- Optional daily scheduler  

---

## 📦 ETL Pipeline Architecture

```
                ┌──────────────────────────┐
                │      watchlist.yaml      │
                │  (list of stock symbols) │
                └─────────────┬────────────┘
                              │
                              ▼
                ┌──────────────────────────┐
                │      Orchestrator        │
                │   (run_pipeline loop)    │
                └─────────────┬────────────┘
                              │
                ┌─────────────┼──────────────┐
                │             │               │
                ▼             ▼               ▼
      ┌────────────────┐  ┌────────────────┐  ┌────────────────┐
      │   Extractor    │  │  Transformer   │  │     Loader     │
      │ fetch_incremental ─▶ transform_data ─▶ load_to_parquet │
      └────────────────┘  └────────────────┘  └────────────────┘
                │                               │
                │                               ▼
                │                     ┌──────────────────────┐
                │                     │  Parquet Dataset     │
                │                     │ partitioned by:      │
                │                     │   • symbol           │
                │                     │   • date             │
                │                     └─────────┬────────────┘
                │                               │
                │                               ▼
                │                     ┌──────────────────────┐
                │                     │      DuckDB SQL      │
                │                     │  parquet_scan() view │
                │                     └─────────┬────────────┘
                │                               │
                ▼                               ▼
      ┌────────────────┐              ┌────────────────────────┐
      │   Logging      │              │   Analytical Queries    │
      │ pipeline.log   │              │  SELECT * FROM ...      │
      └────────────────┘              └────────────────────────┘
```

---

## Running the Pipeline

### **Run once (development mode)**

```bash
python main.py
```

### **Run daily at 18:00 (production mode)**  
Enable the scheduler inside `orchestrator.py` or move it into `main.py`.

---

## Running Tests

```bash
pytest -v
```

Tests cover:
- API extraction  
- Data transformation  
- Parquet writing  
- DuckDB querying  
- Orchestration logic (mocked)  

---

## Environment Variables

Create a `.env` file inside `config/`:

```
ALPHA_VANTAGE_API_KEY=your_api_key_here
```

**Never commit `.env` files.**  
Use `.gitignore` to keep secrets safe.

---

## Dependencies

- Python 3.10+
- pandas
- pyarrow
- duckdb
- requests
- APScheduler
- loguru
- pytest

---

## Future Improvements

- Add CI/CD with GitHub Actions  
- Add data quality checks (Great Expectations)  
- Add dashboarding layer (DuckDB + Polars + Streamlit)  
- Add S3 storage backend for cloud deployment  

---

