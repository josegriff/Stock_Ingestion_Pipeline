import glob
import duckdb
import sys

files = glob.glob("data/**/*.parquet", recursive=True)

if not files:
    print("No parquet files found. Run the pipeline first.")
    sys.exit(1)

con = duckdb.connect("analytics.duckdb")

con.execute("""
    CREATE OR REPLACE VIEW stock_data AS
    SELECT *
    FROM parquet_scan('data/**/*.parquet');
""")

print(con.execute("SELECT COUNT(*) FROM stock_data").fetchall())

print(con.execute("SELECT * FROM stock_data LIMIT 10").df())

print(con.execute("""
    SELECT symbol, COUNT(*) AS rows
    FROM stock_data
    GROUP BY symbol
""").df())

print(con.execute("""
    SELECT symbol, year, month, AVG(Close) AS avg_close
    FROM stock_data
    GROUP BY symbol, year, month
    ORDER BY symbol, year, month
""").df())

print(con.execute("""
    SELECT symbol, MAX(Date) AS latest_date
    FROM stock_data
    GROUP BY symbol
""").df())

print(con.execute("""
WITH yearly AS (
    SELECT
        symbol,
        year,
        FIRST_VALUE(Close) OVER (PARTITION BY symbol, year ORDER BY Date) AS open_year,
        LAST_VALUE(Close) OVER (PARTITION BY symbol, year ORDER BY Date ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS close_year
    FROM stock_data
)
SELECT
    symbol,
    year,
    (close_year - open_year) / open_year AS yearly_return
FROM yearly
GROUP BY symbol, year, open_year, close_year
ORDER BY symbol, year;
""").df())