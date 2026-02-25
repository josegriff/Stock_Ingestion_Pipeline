import glob
import duckdb
import sys

# --- 1. Check that parquet files exist ---
files = glob.glob("data/**/*.parquet", recursive=True)

if not files:
    print("No parquet files found. Run the pipeline first.")
    sys.exit(1)

# --- 2. Connect to DuckDB ---
con = duckdb.connect("analytics.duckdb")

# --- 3. Register parquet lake as a view ---
con.execute("""
    CREATE OR REPLACE VIEW stock_data AS
    SELECT *
    FROM parquet_scan('data/**/*.parquet');
""")

# --- 4. Basic sanity checks ---
print("\n=== TOTAL ROW COUNT ===")
print(con.execute("SELECT COUNT(*) FROM stock_data").fetchall())

print("\n=== SAMPLE ROWS ===")
print(con.execute("SELECT * FROM stock_data LIMIT 10").df())

print("\n=== ROWS PER SYMBOL ===")
print(con.execute("""
    SELECT symbol, COUNT(*) AS rows
    FROM stock_data
    GROUP BY symbol
    ORDER BY symbol
""").df())

print("\n=== LATEST DATE PER SYMBOL ===")
print(con.execute("""
    SELECT symbol, MAX(Date) AS latest_date
    FROM stock_data
    GROUP BY symbol
    ORDER BY symbol
""").df())