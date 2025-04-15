"""
Analysis components for the Gold Market Analysis Dashboard
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple

from utils import calculate_returns
from visualizations import (
    display_profile, display_sequential_patterns, display_barcode_table
)
from help_content import (
    PROFILE_ANALYSIS_HELP, SEQUENTIAL_PATTERNS_HELP, BARCODE_HELP,
    PROFILE_LABELS, TIMEFRAME_LABELS
)

def timeframe_selector(timeframes_loaded: List[str]) -> str:
    """
    Create a timeframe selector dropdown
    
    Args:
        timeframes_loaded: List of loaded timeframes
        
    Returns:
        str: Selected timeframe
    """
    if not timeframes_loaded:
        st.info("No timeframes loaded yet. Please connect to Azure storage and load the data.")
        return None
        
    selected_timeframe = st.selectbox(
        "Select Timeframe", 
        timeframes_loaded,
        index=0,
        help="Choose which timeframe to analyze. Monthly data has the longest history, while shorter timeframes show more recent details."
    )
    
    return selected_timeframe

def date_range_selector(df: pd.DataFrame) -> Tuple[pd.Timestamp, pd.Timestamp]:
    """
    Create date range selection controls
    
    Args:
        df: DataFrame with 'date' column
        
    Returns:
        Tuple[pd.Timestamp, pd.Timestamp]: Selected start and end dates
    """
    if df.empty or 'date' not in df.columns:
        return None, None
        
    min_date = df['date'].min().date()
    max_date = df['date'].max().date()
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date", 
            min_date,
            min_value=min_date,
            max_value=max_date,
            help="Select the starting date for your analysis"
        )
    with col2:
        end_date = st.date_input(
            "End Date", 
            max_date,
            min_value=min_date,
            max_value=max_date,
            help="Select the ending date for your analysis"
        )
        
    # Convert to pandas Timestamp
    start_date = pd.Timestamp(start_date)
    end_date = pd.Timestamp(end_date)
    
    return start_date, end_date

def profile_type_selector() -> str:
    """
    Create a profile type selector dropdown
    
    Returns:
        str: Selected profile type
    """
    profile_options = [
        "decennial", "presidential", "quarter", "month", 
        "week", "week_of_month", "day", "session"
    ]
    
    selected_profile = st.selectbox(
        "Select Profile Type", 
        options=profile_options,
        format_func=lambda x: PROFILE_LABELS.get(x, x),
        help="Choose which cyclical pattern to analyze"
    )
    
    return selected_profile

def display_analysis_content(data_dict: Dict[str, pd.DataFrame], selected_timeframe: str):
    """
    Display the main analysis content with profile section on the main page
    
    Args:
        data_dict: Dictionary of DataFrames for each timeframe
        selected_timeframe: Currently selected timeframe
    """
    # Get selected DataFrame
    df = data_dict.get(selected_timeframe, pd.DataFrame())
    
    if df.empty:
        st.info("Selected dataframe is empty. Try another timeframe.")
        return
        
    # Create controls at the top of the page
    st.markdown("## Analysis Settings")
    settings_col1, settings_col2 = st.columns(2)
    
    with settings_col1:
        # Date range selection moved to main page
        start_date, end_date = date_range_selector(df)
        
    with settings_col2:
        # Profile type selection moved to main page
        selected_profile = profile_type_selector()
    
    # Analysis section with tabs
    st.markdown("## Market Analysis Results")
    
    # Create analysis tabs
    tab1, tab2, tab3 = st.tabs(["📊 Profile Analysis", "🔄 Sequential Patterns", "📋 Historic Barcode"])
    
    with tab1:
        # Info box for profile analysis
        st.info(PROFILE_ANALYSIS_HELP)
        
        # Display selected profile
        display_profile(
            data_dict, 
            selected_profile, 
            selected_timeframe, 
            start_date, 
            end_date
        )
    
    with tab2:
        # Info box for sequential patterns
        st.info(SEQUENTIAL_PATTERNS_HELP)
        
        # Process data for pattern detection
        filtered_df = df[(df['date'] >= start_date) & (df['date'] <= end_date)].copy()
        
        if len(filtered_df) > 0:
            # Add required columns for pattern analysis
            filtered_df = calculate_returns(filtered_df)
            
            # Pattern length selection
            pattern_length = st.slider(
                "Pattern Length", 
                min_value=2, 
                max_value=5, 
                value=3,
                help="Select how many consecutive periods to include in each pattern"
            )
            
            # Display patterns
            display_sequential_patterns(filtered_df, 'is_green', pattern_length=pattern_length)
        else:
            st.warning("Not enough data for pattern analysis in the selected date range.")
    
    with tab3:
        # Info box for barcode
        st.info(BARCODE_HELP)
        
        # Date selection for barcode
        barcode_date = st.date_input(
            "Select Reference Date", 
            end_date.date() - timedelta(days=365),
            min_value=start_date.date(),
            max_value=end_date.date(),
            help="Choose a date to center your barcode view around"
        )
        
        # Display barcode profile
        display_barcode_table(data_dict, selected_timeframe, barcode_date)

def analysis_section():
    """
    Display the data analysis section - only shown when monthly data is loaded
    """
    # Continue bulk loading in the background if requested
    if st.session_state.load_requested and not st.session_state.loading_complete:
        from data_loading import load_next_timeframe
        load_next_timeframe()
    
    # Create the timeframe selector at the top
    selected_timeframe = timeframe_selector(st.session_state.timeframes_loaded)
    
    if selected_timeframe:
        # Display the analysis content
        display_analysis_content(st.session_state.data_dict, selected_timeframe)
