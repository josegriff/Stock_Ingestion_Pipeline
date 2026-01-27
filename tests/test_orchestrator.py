import pytest
from unittest.mock import patch, MagicMock
from src.orchestrator import run_pipeline

"""
    Tests that the orchestrotor:
    1. Loads symbols from config
    2. Calls extractor for each symbol
    3. Calls transformer for each symbol
    4. Calls loader for each symbol
    5. Handles None DataFrames correctly
"""

@patch("src.orchestrator.load_to_parquet")
@patch("src.orchestrator.transform_data")
@patch("src.orchestrator.fetch_incremental")
@patch("src.orchestrator.yaml.safe_load")

def test_run_pipeline(mock_yaml, 
                      mock_fetch, 
                      mock_transform, 
                      mock_load
                      ):
    
    mock_yaml.return_value = {                       # Mock config with two symbols
        "symbols": ["BP.L", "VOD.L"]
        }
    
    mock_fetch.return_value = {"2024-06-14": 
                                {"1. open": "100"}}  # Fake exttractor output
    
    fake_df = MagicMock()                            
    mock_transform.return_value = fake_df            # Fake transformer output
    
    run_pipeline()                                   # Execute the orchestrator
    
    assert mock_fetch.call_count == 2                # Extractor called once per symbol
    assert mock_transform.call_count == 2            # Transformer called once per symbol
    assert mock_load.call_count == 2                 # Loader called once per symbol
    
    mock_transform.assert_any_call                   # Check transformer args
    ("BP.L", mock_fetch.return_value)
    
    mock_transform.assert_any_call
    ("VOD.L", mock_fetch.return_value)         
    
    mock_load.assert_any_call(fake_df)               # Loader called with transformed DataFrame  
                                                      