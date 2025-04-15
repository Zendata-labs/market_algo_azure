"""
Gold Market Analysis Dashboard - Main Application
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import time

# Import our modules
from utils import load_data_from_azure, calculate_returns, calculate_atr, categorize_atr, get_sequential_patterns
from config import timeframe_files
from visualizations import (
    apply_styling, create_header, display_profile, 
    display_barcode_table, display_sequential_patterns
)
# Import new modular components
from data_loading import connection_section
from analysis import analysis_section
from help_content import USER_GUIDE, INTERPRETATION_GUIDE

# Set page configuration
st.set_page_config(
    page_title="Gold Market Analysis", 
    page_icon="📈", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables
if 'data_dict' not in st.session_state:
    st.session_state.data_dict = {}
if 'loading_complete' not in st.session_state:
    st.session_state.loading_complete = False
if 'loading_status' not in st.session_state:
    st.session_state.loading_status = {}
if 'timeframes_loaded' not in st.session_state:
    st.session_state.timeframes_loaded = []
if 'next_timeframe_to_load' not in st.session_state:
    st.session_state.next_timeframe_to_load = 0
if 'load_requested' not in st.session_state:
    st.session_state.load_requested = False

def main():
    """
    Main function to run the Streamlit app
    """
    # Apply styling
    apply_styling()
    
    # Create header
    create_header()
    
    # Connection and data loading container - main part of the UI flow
    connection_container = st.container()
    with connection_container:
        connection_section()
    
    # Only show analysis section if monthly data is loaded
    if hasattr(st.session_state, 'data_loaded') and st.session_state.data_loaded:
        # Create tabs for analysis
        st.markdown("---")
        analysis_tabs = st.tabs(["📊 Market Analysis", "📚 Help & Guide"])
        
        with analysis_tabs[0]:
            # Show the analysis section with profile on main page
            analysis_section()
            
        with analysis_tabs[1]:
            st.markdown("# Gold Market Analysis Dashboard - User Guide")
            
            st.markdown(USER_GUIDE)
            
            # Add detailed explanations with examples
            with st.expander("How to Interpret Results"):
                st.markdown(INTERPRETATION_GUIDE)

if __name__ == "__main__":
    main()