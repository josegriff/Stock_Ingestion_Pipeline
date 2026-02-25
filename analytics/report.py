import duckdb
import re
import time

# Connect to DuckDB
con = duckdb.connect("analytics.duckdb")

# Register the parquet lake as a view
con.execute("""
    CREATE OR REPLACE VIEW stock_data AS
    SELECT *
    FROM parquet_scan('data/**/*.parquet');
""")

# Load SQL file
with open("analytics/queries.sql", "r") as f:
    sql_text = f.read()

# Split queries on semicolons
raw_queries = [q.strip() for q in sql_text.split(";") if q.strip()]

# Extract titles from comments
def extract_title(query_text):
    match = re.search(r"--\s*\d+\.\s*(.+)", query_text)
    return match.group(1).strip() if match else "Untitled Query"

queries = [(extract_title(q), q) for q in raw_queries]

print("\n=== Running Analytics Queries ===\n")

for i, (title, query) in enumerate(queries, start=1):
    print(f"\n--- Query {i}. {title} ---")

    start = time.time()  # ⬅️ Start timer

    try:
        result = con.execute(query).df()

        # Sort newest first if Date column exists
        if "Date" in result.columns:
            result = result.sort_values("Date", ascending=False)

        # Interleave symbols if present
        if "symbol" in result.columns:
            result["row_id"] = result.groupby("symbol").cumcount()
            result = result.sort_values(["row_id", "symbol"]).drop(columns=["row_id"])

        # Print a meaningful sample
        print(result.head(10))
        print(f"[{len(result)} rows x {len(result.columns)} columns]")

    except Exception as e:
        print(f"Error executing query {i}: {e}")

    end = time.time()  # ⬅️ End timer
    print(f"Execution time: {end - start:.3f} seconds")

print("\nAll queries executed.\n")