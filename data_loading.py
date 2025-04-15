"""
Data loading functions for the Gold Market Analysis Dashboard
"""

import streamlit as st
import time
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from config import timeframe_files
from utils import load_data_from_azure
from ui_components import (
    create_connection_card, create_monthly_data_card, create_bulk_loading_card,
    loading_button, simulate_progress, create_timeframe_status_table,
    show_bulk_loading_progress, reset_button_state, TIMEFRAME_LABELS
)
from help_content import DATA_LOADING_HELP

def load_monthly_data() -> bool:
    """
    Load only the monthly data initially
    
    Returns:
        bool: True if loading succeeded, False otherwise
    """
    try:
        monthly_file = "M.csv"
        st.session_state.data_dict["M"] = load_data_from_azure(monthly_file)
        st.session_state.timeframes_loaded.append("M")
        st.session_state.loading_status["M"] = "Loaded"
        return True
    except Exception as e:
        st.error(f"Error loading monthly data: {str(e)}")
        return False

def load_next_timeframe() -> bool:
    """
    Load the next timeframe in the sequence
    
    Returns:
        bool: True if a timeframe was loaded, False if all are done
    """
    # Get reversed list of timeframes (largest to smallest)
    sorted_timeframes = list(reversed(timeframe_files))
    
    # If we've loaded all timeframes, mark as complete
    if st.session_state.next_timeframe_to_load >= len(sorted_timeframes):
        st.session_state.loading_complete = True
        return False
    
    # Get the next timeframe to load
    file = sorted_timeframes[st.session_state.next_timeframe_to_load]
    timeframe = file.split('.')[0]
    
    # Skip monthly which is already loaded
    if timeframe == "M":
        st.session_state.next_timeframe_to_load += 1
        return False
        
    try:
        st.session_state.loading_status[timeframe] = "Loading..."
        st.session_state.data_dict[timeframe] = load_data_from_azure(file)
        st.session_state.timeframes_loaded.append(timeframe)
        st.session_state.loading_status[timeframe] = "Loaded"
    except Exception as e:
        st.session_state.loading_status[timeframe] = f"Error: {str(e)}"
    
    # Move to next timeframe
    st.session_state.next_timeframe_to_load += 1
    return True

def get_remaining_timeframes() -> List[str]:
    """
    Get list of remaining timeframes to load
    
    Returns:
        List[str]: List of timeframe codes not yet loaded
    """
    return [
        tf.split('.')[0] for tf in reversed(timeframe_files) 
        if tf.split('.')[0] != "M" and tf.split('.')[0] not in st.session_state.timeframes_loaded
    ]

def load_specific_timeframe(timeframe: str) -> bool:
    """
    Load a specific timeframe
    
    Args:
        timeframe: Timeframe code to load
        
    Returns:
        bool: True if loading succeeded, False otherwise
    """
    try:
        file_name = next((f for f in timeframe_files if f.startswith(timeframe)), None)
        if not file_name:
            return False
        
        st.session_state.loading_status[timeframe] = "Loading..."
        st.session_state.data_dict[timeframe] = load_data_from_azure(file_name)
        
        if timeframe not in st.session_state.timeframes_loaded:
            st.session_state.timeframes_loaded.append(timeframe)
            
        st.session_state.loading_status[timeframe] = "Loaded"
        return True
    except Exception as e:
        st.session_state.loading_status[timeframe] = f"Error: {str(e)}"
        return False

def connection_section():
    """
    Display Azure Blob storage connection UI with improved loading experience
    """
    # Initial connection section
    st.markdown("<h2>Gold Market Analysis Dashboard</h2>", unsafe_allow_html=True)
    st.markdown("""
    Welcome to the Gold Market Analysis Dashboard. This tool helps you analyze gold market patterns
    across different timeframes. Follow these steps to get started:
    
    1. Connect to Azure Storage 
    2. Load Monthly data
    3. Then load additional timeframes as needed
    """)
    
    # Connection button in a container
    with st.container():
        connect_col1, connect_col2 = st.columns([3, 2])
        
        with connect_col1:
            create_connection_card()
        
        with connect_col2:
            def connect_callback():
                time.sleep(1)  # Simulate connection time
                st.session_state["connected"] = True
                reset_button_state("connect_btn")
                
            # Only show button if not connected yet
            if "connected" not in st.session_state:
                loading_button(
                    "1️⃣ Connect to Azure Storage", 
                    "connect_btn", 
                    connect_callback,
                    use_container_width=True
                )
            else:
                st.success("✅ Successfully connected to Azure Blob Storage!")

    # If user clicked connect or was already connected
    if "connected" in st.session_state:
        # Data loading section - separate from connection
        st.markdown("---")
        st.markdown("<h3>Data Loading Center</h3>", unsafe_allow_html=True)
        
        # Info message about loading sequence
        st.info(DATA_LOADING_HELP)
        
        # Monthly data loading first - in its own container
        with st.container():
            if "M" not in st.session_state.timeframes_loaded:
                monthly_col1, monthly_col2 = st.columns([3, 2])
                
                with monthly_col1:
                    create_monthly_data_card()
                
                with monthly_col2:
                    def load_monthly_callback():
                        # Create a progress bar
                        progress_bar = st.progress(0, text="Starting monthly data load...")
                        
                        # Simulate progress for better UX
                        simulate_progress(
                            progress_bar,
                            "Starting monthly data load...",
                            {
                                25: "Connecting to storage...",
                                50: "Retrieving monthly data...",
                                75: "Processing monthly data..."
                            }
                        )
                            
                        # Now actually load the data 
                        success = load_monthly_data()
                        
                        if success:
                            st.session_state["data_loaded"] = True
                            st.success("✅ Monthly (M) data loaded successfully!")
                            reset_button_state("monthly_btn")
                            st.rerun()
                        else:
                            st.error("❌ Failed to load Monthly data. Please check your connection and try again.")
                            reset_button_state("monthly_btn")
                            
                    loading_button(
                        "2️⃣ Load Monthly Data", 
                        "monthly_btn", 
                        load_monthly_callback,
                        use_container_width=True
                    )
            else:
                st.success("✅ Monthly (M) data loaded")
                
                # Show remaining timeframes to load
                remaining_timeframes = get_remaining_timeframes()
                
                # Loading options section
                st.markdown("### Additional Timeframes")
                
                # Check if we still have timeframes to load
                if remaining_timeframes:
                    st.markdown(f"**{len(remaining_timeframes)} timeframes remaining to load**")
                    
                    # Option to load all remaining timeframes
                    if not st.session_state.loading_complete and not st.session_state.load_requested:
                        all_col1, all_col2 = st.columns([3, 2])
                        
                        with all_col1:
                            create_bulk_loading_card()
                            
                        with all_col2:
                            def load_all_callback():
                                st.session_state.load_requested = True
                                st.info("🔄 Starting progressive loading of additional timeframes...")
                                reset_button_state("load_all_btn")
                                st.rerun()
                                
                            loading_button(
                                "3️⃣ Load All Remaining Timeframes", 
                                "load_all_btn", 
                                load_all_callback,
                                use_container_width=True
                            )
                    
                    # Show individual loading buttons for each remaining timeframe
                    st.markdown("#### Or load individual timeframes:")
                    
                    # Create 2 columns for individual loading buttons
                    col_left, col_right = st.columns(2)
                    
                    # Find next timeframe to load if not bulk loading
                    if not st.session_state.load_requested:
                        for i, tf in enumerate(remaining_timeframes):
                            # Alternate between columns
                            with col_left if i % 2 == 0 else col_right:
                                # Get the actual filename
                                file_name = next((f for f in timeframe_files if f.startswith(tf)), None)
                                
                                if file_name:
                                    friendly_name = TIMEFRAME_LABELS.get(tf, tf)
                                    
                                    def make_callback(timeframe):
                                        def callback():
                                            # Create container for this timeframe's loading progress
                                            st.markdown(f"**Loading {friendly_name} ({timeframe}):**")
                                            progress_bar = st.progress(0, text=f"Starting {timeframe} data load...")
                                            
                                            # Update progress in stages
                                            simulate_progress(
                                                progress_bar,
                                                f"Starting {timeframe} data load...",
                                                {
                                                    30: f"Retrieving {timeframe} data...",
                                                    60: f"Processing {timeframe} data...",
                                                    90: f"Almost done..."
                                                }
                                            )
                                            
                                            # Now actually load the data
                                            success = load_specific_timeframe(timeframe)
                                            
                                            # Force rerun to update UI
                                            if success:
                                                st.success(f"✅ {friendly_name} ({timeframe}) data loaded successfully!")
                                            else:
                                                st.error(f"❌ Failed to load {friendly_name} data")
                                                
                                            reset_button_state(f"load_{tf}_btn")
                                            time.sleep(0.5)  # Small delay to show success message
                                            st.rerun()
                                        return callback
                                    
                                    loading_button(
                                        f"Load {friendly_name} Data", 
                                        f"load_{tf}_btn",
                                        make_callback(tf),
                                        use_container_width=True
                                    )
                    
                    # If bulk loading is in progress, show the current progress
                    elif st.session_state.load_requested and not st.session_state.loading_complete:
                        # Create a container for bulk loading progress
                        with st.container():
                            show_bulk_loading_progress(
                                timeframe_files, 
                                st.session_state.timeframes_loaded,
                                st.session_state.next_timeframe_to_load
                            )
                else:
                    st.success("✅ All timeframes have been loaded!")
                
        # Always show the loading status/progress table at the bottom
        with st.container():
            st.markdown("---")
            st.markdown("### Data Loading Status")
            
            create_timeframe_status_table(
                timeframe_files,
                st.session_state.loading_status
            )
