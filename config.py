# config.py
import os
import streamlit as st
from dotenv import load_dotenv

# Try multiple approaches to get secrets, with fallbacks

# First try to load from top-level Streamlit secrets
try:
    AZURE_STORAGE_CONNECTION_STRING = st.secrets["AZURE_STORAGE_CONNECTION_STRING"]
    CONTAINER_NAME = st.secrets["CONTAINER_NAME"]
    print("Loaded configuration from top-level Streamlit secrets")
except Exception as e1:
    try:
        # Next try the azure section in Streamlit secrets
        AZURE_STORAGE_CONNECTION_STRING = st.secrets["azure"]["storage_connection_string"]
        CONTAINER_NAME = st.secrets["azure"]["container_name"]
        print("Loaded configuration from azure section in Streamlit secrets")
    except Exception as e2:
        # Finally fall back to .env file (for local development)
        print(f"Couldn't load from Streamlit secrets. Trying .env file...")
        load_dotenv()
        AZURE_STORAGE_CONNECTION_STRING = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
        CONTAINER_NAME = os.getenv('CONTAINER_NAME')
        
        if not AZURE_STORAGE_CONNECTION_STRING:
            print("Warning: Azure Storage connection string not found in any location")

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
