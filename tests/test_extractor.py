import pytest
from src.extractor import fetch_stock_data

def tech_fetch_stock_data():
    data = fetch_stock_data("BP.L")
    assert "Time Series (Daily)" in data # Basic check for expected key
    assert isinstance(data, dict)        # Ensure returned data is a dictionary  