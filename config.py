# config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get sensitive information from environment variables
AZURE_STORAGE_CONNECTION_STRING = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
CONTAINER_NAME = os.getenv('CONTAINER_NAME')

# Define dataset file paths in Azure Storage
timeframe_files = [
    "1min.csv",
    "5min.csv",
    "10min.csv",
    "15min.csv",
    "30min.csv",
    "1h.csv",
    "4h.csv",
    "D.csv",
    "W.csv",
    "M.csv"
]

# Define column names mapping (from original to standardized)
column_mapping = {
    'Date': 'date',
    'Symbol': 'symbol',
    'Open': 'open',
    'High': 'high',
    'Low': 'low',
    'Close': 'close',
    'Volume': 'volume'
}

# Chart color settings
chart_colors = {
    'green': 'rgba(46, 125, 50, 0.7)',  # For green candles/bars
    'red': 'rgba(211, 47, 47, 0.7)',    # For red candles/bars
    'blue': 'rgba(33, 150, 243, 0.7)',  # For return lines
    'gold': '#ffd700'                   # For accent elements
}
