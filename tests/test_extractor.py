import pytest
from src.extractor import fetch_stock_data

def test_fetch_stock_data():
    data = fetch_stock_data("BP.L")
    
    assert isinstance(data, dict)           # Ensure returned data is a dictionary 
    assert "Time Series (Daily)" in data    # Basic check for expected key  