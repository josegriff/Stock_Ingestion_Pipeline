"""
Purpose of main.py:
Entry point for the ETL pipeline.
Runs the pipeline immediately on demand.
"""

from loguru import logger
from src.orchestrator import run_pipeline

if __name__ == "__main__":
    logger.info("Running pipeline...")
    run_pipeline()
    logger.info("Pipeline finished.")
    
# tree data /F prints every folder and parwuet file in data/ dir