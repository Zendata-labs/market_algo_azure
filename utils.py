import os
import pandas as pd
import numpy as np
from datetime import datetime
import pytz
from azure.storage.blob import BlobServiceClient
import streamlit as st
from config import AZURE_STORAGE_CONNECTION_STRING, CONTAINER_NAME, timeframe_files, column_mapping
import asyncio

# Fix for the coroutine warning
try:
    # Create a new event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
except RuntimeError:
    pass

# Cache the data loading to improve performance
@st.cache_data(ttl=3600)
def load_data_from_local(file_name):
    """
    Load data from local CSV files
    """
    try:
        # Construct the path to the CSV file
        file_path = os.path.join(os.getcwd(), file_name)
        
        # Read the CSV file
        df = pd.read_csv(file_path)
        
        # Filter for gold data (symbols starting with 'GC')
        if 'Symbol' in df.columns:
            df = df[df['Symbol'].str.startswith('GC')]
        
        # Ensure date column is datetime
        if 'Date' in df.columns:
            df['date'] = pd.to_datetime(df['Date'])
            # Drop the original 'Date' column
            df = df.drop('Date', axis=1)
        
        # Handle numeric columns with commas
        for col in ['Open', 'High', 'Low', 'Close']:
            if col in df.columns:
                # Replace commas and convert to float
                df[col.lower()] = df[col].astype(str).str.replace(',', '').astype(float)
                # Drop the original column if it's different from the lowercase version
                if col != col.lower():
                    df = df.drop(col, axis=1)
        
        # Keep only necessary columns and rename them
        cols_to_keep = ['date']
        if 'Symbol' in df.columns:
            cols_to_keep.append('Symbol')
            df = df.rename(columns={'Symbol': 'symbol'})
        
        for col in ['open', 'high', 'low', 'close']:
            if col in df.columns:
                cols_to_keep.append(col)
            
        # Filter to only needed columns
        df = df[cols_to_keep]
            
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def load_data_from_azure(file_name):
    """
    Load data from Azure Blob Storage
    """
    try:
        # Verify connection string is available
        if not AZURE_STORAGE_CONNECTION_STRING:
            raise ValueError("Azure Storage connection string is not available. Check your .env file or Streamlit secrets.")
            
        # Print the first few characters to debug (without revealing the full key)
        safe_connection_str = AZURE_STORAGE_CONNECTION_STRING[:30] + '...' if AZURE_STORAGE_CONNECTION_STRING else 'None'
        print(f"Connection string (truncated): {safe_connection_str}")
        print(f"Container name: {CONTAINER_NAME}")
        print(f"Loading file: {file_name}")
        
        # Create client and download data
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
        container_client = blob_service_client.get_container_client(CONTAINER_NAME)
        blob_client = container_client.get_blob_client(file_name)
        
        # Download the blob data as a string
        download_stream = blob_client.download_blob()
        data = download_stream.readall()
        
        # Convert to pandas DataFrame
        df = pd.read_csv(pd.io.common.BytesIO(data))
        
        # Filter for gold data (symbols starting with 'GC')
        if 'Symbol' in df.columns:
            df = df[df['Symbol'].str.startswith('GC')]
        
        # Handle date column (capital 'Date' vs lowercase 'date')
        if 'Date' in df.columns:
            df['date'] = pd.to_datetime(df['Date'])
            df = df.drop('Date', axis=1)
        elif 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        
        # Handle numeric columns with commas
        for col in ['Open', 'High', 'Low', 'Close']:
            if col in df.columns:
                # Replace commas and convert to float
                df[col.lower()] = df[col].astype(str).str.replace(',', '').astype(float)
                # Drop the original column if it's different from the lowercase version
                if col != col.lower():
                    df = df.drop(col, axis=1)
                    
        # Keep only necessary columns
        columns_to_keep = ['date']
        for col in ['symbol', 'open', 'high', 'low', 'close']:
            if col in df.columns:
                columns_to_keep.append(col)
        
        # Make sure we have all the columns we need
        df = df.rename(columns={
            'Symbol': 'symbol',
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close'
        })
        
        # Keep only needed columns
        columns_present = [col for col in columns_to_keep if col in df.columns]
        df = df[columns_present]
            
        return df
    except Exception as e:
        st.error(f"Error loading data from Azure: {str(e)}")
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def load_all_timeframes():
    """
    Load all timeframe data and return as a dictionary
    """
    data_dict = {}
    # Load in reverse order (monthly to 1min) as per requirement
    for file in reversed(timeframe_files):
        timeframe = file.split('.')[0]
        data_dict[timeframe] = load_data_from_azure(file)
    return data_dict

def calculate_atr(df, period=14):
    """
    Calculate Average True Range (ATR)
    """
    high = df['high'].values
    low = df['low'].values
    close = np.array(df['close'].values[:-1])  # Previous close
    
    # Insert a NaN at the beginning of close to align with current day
    close = np.insert(close, 0, np.nan)
    
    # Calculate True Range
    tr1 = np.abs(high - low)
    tr2 = np.abs(high - close)
    tr3 = np.abs(low - close)
    
    # True Range is the max of the three
    tr = np.maximum(np.maximum(tr1, tr2), tr3)
    
    # Calculate ATR
    atr = pd.Series(tr).rolling(window=period).mean().values
    
    return atr

def categorize_atr(atr_values, thresholds=(0.33, 0.67)):
    """
    Categorize ATR values into 1 (low), 2 (average), or 3 (high)
    """
    # Remove NaN values for percentile calculation
    clean_atr = atr_values[~np.isnan(atr_values)]
    
    if len(clean_atr) == 0:
        return np.full_like(atr_values, np.nan)
    
    # Calculate thresholds based on percentiles
    low_threshold = np.percentile(clean_atr, thresholds[0] * 100)
    high_threshold = np.percentile(clean_atr, thresholds[1] * 100)
    
    # Categorize values
    categories = np.full_like(atr_values, 2, dtype=float)  # Default to category 2 (average)
    categories[atr_values <= low_threshold] = 1  # Low volatility
    categories[atr_values >= high_threshold] = 3  # High volatility
    categories[np.isnan(atr_values)] = np.nan  # Keep NaNs as NaNs
    
    return categories

def calculate_returns(df):
    """
    Calculate daily returns and determine if day was green or red
    """
    df = df.copy()  # Create a copy to avoid modifying the original dataframe
    df['return'] = df['close'].pct_change() * 100
    df['is_green'] = df['close'] > df['open']
    return df

def filter_data_by_timeframe(df, timeframe, start_date=None, end_date=None):
    """
    Filter data by given timeframe and date range
    """
    df = df.copy()
    
    # Apply date range filter if specified
    if start_date:
        df = df[df['date'] >= start_date]
    if end_date:
        df = df[df['date'] <= end_date]
        
    return df

def get_sequential_patterns(series, pattern_length=3):
    """
    Find sequential patterns in a series
    """
    patterns = []
    for i in range(len(series) - pattern_length + 1):
        pattern = tuple(series.iloc[i:i+pattern_length])
        patterns.append(pattern)
    
    # Count occurrences of each pattern
    pattern_counts = {}
    for pattern in patterns:
        if pattern in pattern_counts:
            pattern_counts[pattern] += 1
        else:
            pattern_counts[pattern] = 1
    
    # Sort by frequency
    sorted_patterns = sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)
    
    return sorted_patterns

def prepare_profile_data(df, profile_type, filter_params=None):
    """
    Prepare data for different profile types
    """
    df = df.copy()
    
    # Add necessary calculations
    df = calculate_returns(df)
    atr_values = calculate_atr(df)
    df['atr'] = atr_values
    df['atr_category'] = categorize_atr(atr_values)
    
    # Filter if needed
    if filter_params:
        df = filter_data_by_timeframe(df, **filter_params)
    
    # Create profile-specific grouping
    if profile_type == 'decennial':
        # Group by the last digit of the year (0-9)
        df['group'] = df['date'].dt.year % 10
        group_name = 'Year Digit'
        
    elif profile_type == 'presidential':
        # Presidential cycle (years 1-4)
        # Adjust years to fit 1-4 cycle
        df['group'] = ((df['date'].dt.year - 1) % 4) + 1
        group_name = 'Presidential Year'
        
    elif profile_type == 'quarter':
        # Quarter (1-4)
        df['group'] = df['date'].dt.quarter
        group_name = 'Quarter'
        
    elif profile_type == 'month':
        # Month (1-12)
        df['group'] = df['date'].dt.month
        group_name = 'Month'
        
    elif profile_type == 'week':
        # Week of year (1-52/53)
        df['group'] = df['date'].dt.isocalendar().week
        group_name = 'Week of Year'
        
    elif profile_type == 'week_of_month':
        # Week of month (1-4/5)
        # Calculate week of month by dividing day by 7 and rounding up
        df['group'] = np.ceil(df['date'].dt.day / 7).astype(int)
        group_name = 'Week of Month'
        
    elif profile_type == 'day':
        # Day of week (1-5 for trading days)
        df['group'] = df['date'].dt.dayofweek + 1  # 1 for Monday, 5 for Friday
        df = df[df['group'] <= 5]  # Filter out weekends
        group_name = 'Day of Week'
        
    elif profile_type == 'session':
        # Trading session (0=pre-market, 1=regular, 2=post-market)
        # Assuming regular market hours are 9:30 AM to 4:00 PM ET
        # This calculation depends on having time data
        ny_tz = pytz.timezone('America/New_York')
        
        def determine_session(row):
            hour = row['date'].hour
            minute = row['date'].minute
            time_val = hour * 60 + minute  # Time in minutes
            
            if time_val < 9*60 + 30:  # Before 9:30 AM
                return 0  # Pre-market
            elif time_val < 16*60:  # Before 4:00 PM
                return 1  # Regular session
            else:
                return 2  # Post-market
                
        if 'time' in df.columns or (isinstance(df['date'].iloc[0], pd.Timestamp) and df['date'].iloc[0].time() != datetime.min.time()):
            df['group'] = df.apply(determine_session, axis=1)
        else:
            # If no time data, default to regular session
            df['group'] = 1
        
        group_name = 'Trading Session'
        
    # Aggregate data by group
    agg_data = df.groupby('group').agg({
        'is_green': 'mean',  # Probability of green (1 = 100%)
        'return': ['mean', 'std'],  # Average return and standard deviation
        'atr': 'mean',  # Average ATR
        'atr_category': lambda x: pd.Series.mode(x)[0] if not pd.Series.mode(x).empty else np.nan  # Most common ATR category
    })
    
    # Flatten multi-index columns
    agg_data.columns = ['green_probability', 'avg_return', 'return_std', 'avg_atr', 'most_common_atr']
    
    # Calculate additional metrics
    agg_data['red_probability'] = 1 - agg_data['green_probability']
    
    # Calculate average loss for red days and average gain for green days
    green_returns = {}
    red_returns = {}
    
    for group in df['group'].unique():
        group_df = df[df['group'] == group]
        green_days = group_df[group_df['is_green']]
        red_days = group_df[~group_df['is_green']]
        
        green_returns[group] = green_days['return'].mean() if not green_days.empty else 0
        red_returns[group] = red_days['return'].mean() if not red_days.empty else 0
    
    agg_data['avg_green_return'] = pd.Series(green_returns)
    agg_data['avg_red_return'] = pd.Series(red_returns)
    
    # Reset index to make group a column
    agg_data = agg_data.reset_index()
    agg_data.rename(columns={'group': group_name}, inplace=True)
    
    return agg_data

def get_bar_count(profile_type):
    """
    Return the expected number of bars for each profile type
    """
    bar_counts = {
        'decennial': 10,
        'presidential': 4,
        'quarter': 4,
        'month': 12,
        'week': 52,
        'week_of_month': 4,
        'day': 5,
        'session': 3
    }
    return bar_counts.get(profile_type, 0)
