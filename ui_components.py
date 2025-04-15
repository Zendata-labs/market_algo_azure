"""
UI components and interactive elements for the Gold Market Analysis Dashboard
"""

import streamlit as st
import time
from typing import Callable, Optional, Dict, List, Any
import pandas as pd
from help_content import TIMEFRAME_LABELS

def create_help_box(title: str, content: str, location=st):
    """
    Create a collapsible help box with explanations
    
    Args:
        title: Title of the help box
        content: Markdown content to display
        location: Streamlit container to place the expander in (default: st)
    """
    with location.expander(f"ℹ️ {title}"):
        location.markdown(content)

def create_connection_card():
    """
    Display Azure Blob storage connection information card
    """
    st.markdown("""
    <div style="padding: 20px; border-radius: 10px; background-color: #212121; border-left: 5px solid #ffd700;">
        <h4 style="color: #ffd700;">Azure Blob Storage</h4>
        <p>This app connects to Azure Blob Storage to retrieve gold market data for analysis.</p>
        <ul>
            <li>Container: <code>gold</code></li>
            <li>Account: <code>marketalgo</code></li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

def create_monthly_data_card():
    """
    Display the monthly data loading card
    """
    st.markdown("""
    <div style="padding: 15px; border-radius: 5px; background-color: #1e1e1e; margin-bottom: 10px;">
        <h4>Monthly Timeframe</h4>
        <p>Load monthly data first to establish the baseline dataset for analysis.</p>
        <p><em>This is required before loading other timeframes.</em></p>
    </div>
    """, unsafe_allow_html=True)

def create_bulk_loading_card():
    """
    Display the bulk loading information card
    """
    st.markdown("""
    <div style="padding: 15px; border-radius: 5px; background-color: #1e1e1e; margin-bottom: 10px;">
        <h4>Bulk Loading</h4>
        <p>Load all remaining timeframes automatically in sequence.</p>
        <p><em>This will take a few minutes to complete.</em></p>
    </div>
    """, unsafe_allow_html=True)

def loading_button(label: str, key: str, on_click: Callable, args: tuple = (), 
                   disabled: bool = False, type: str = "primary",
                   use_container_width: bool = True) -> bool:
    """
    Create a button that shows loading state and prevents multiple clicks
    
    Args:
        label: Button label
        key: Unique key for the button
        on_click: Function to call when button is clicked
        args: Arguments to pass to the on_click function
        disabled: Whether the button should be disabled
        type: Button type (primary, secondary)
        use_container_width: Whether to use full container width
        
    Returns:
        True if the button was clicked, False otherwise
    """
    # Create button state key if it doesn't exist
    button_state_key = f"{key}_state"
    if button_state_key not in st.session_state:
        st.session_state[button_state_key] = "ready"
    
    # Set callback
    def handle_click():
        if st.session_state[button_state_key] == "ready":
            st.session_state[button_state_key] = "loading"
            on_click(*args)
    
    # Show different button based on state
    if st.session_state[button_state_key] == "loading":
        placeholder = st.empty()
        with placeholder:
            st.button(
                f"Loading... ⏳", 
                key=f"{key}_loading", 
                disabled=True,
                type=type,
                use_container_width=use_container_width
            )
        return True
    else:
        clicked = st.button(
            label, 
            key=key, 
            on_click=handle_click, 
            disabled=disabled,
            type=type,
            use_container_width=use_container_width
        )
        return clicked

def simulate_progress(progress_bar, start_message: str = "Starting...", 
                     middle_messages: Dict[int, str] = None,
                     end_message: str = "Complete"):
    """
    Simulate a progress bar with messages at different points
    
    Args:
        progress_bar: Streamlit progress bar
        start_message: Initial message to show
        middle_messages: Dict mapping progress percentage to message
        end_message: Final message to show
    """
    if middle_messages is None:
        middle_messages = {
            25: "Processing...",
            50: "Retrieving data...",
            75: "Almost done..."
        }
    
    # Start with initial message
    progress_bar.progress(0, text=start_message)
    
    # Update progress with messages at specified points
    for i in range(1, 101):
        if i in middle_messages:
            progress_bar.progress(i/100, text=middle_messages[i])
        elif i == 100:
            progress_bar.progress(i/100, text=end_message)
        else:
            progress_bar.progress(i/100)
        time.sleep(0.01)  # Fast enough to not be annoying

def create_timeframe_status_table(timeframe_files: List[str], loading_status: Dict[str, str]):
    """
    Create a status table showing the loading status of each timeframe
    
    Args:
        timeframe_files: List of timeframe files
        loading_status: Dict mapping timeframe to loading status
    """
    # Create columns for the status table
    status_cols = st.columns([3, 7])
    
    with status_cols[0]:
        st.markdown("**Timeframe**")
    with status_cols[1]:
        st.markdown("**Status**")
        
    # Draw separator
    st.markdown("<hr style='margin: 5px 0; border-top: 1px solid #333'>", unsafe_allow_html=True)
    
    # Create a status row for each timeframe
    for file in reversed(timeframe_files):
        timeframe = file.split('.')[0]
        friendly_name = TIMEFRAME_LABELS.get(timeframe, timeframe)
        
        status = loading_status.get(timeframe, "Not loaded")
        
        # Determine progress and color based on status
        if status == "Loaded":
            status_color = "green"
            progress = 100
            icon = "✅"
        elif status == "Loading...":
            status_color = "blue"
            progress = 50
            icon = "🔄"
        elif status.startswith("Error"):
            status_color = "red"
            progress = 100
            icon = "❌"
            error_msg = status[7:]  # Remove "Error: " prefix
        else:
            status_color = "gray"
            progress = 0
            icon = "⏸️"
        
        # Create status row
        row_cols = st.columns([3, 7])
        
        with row_cols[0]:
            st.markdown(f"**{friendly_name} ({timeframe})**")
            
        with row_cols[1]:
            # Show progress bar or error message
            if status.startswith("Error"):
                st.markdown(f"<span style='color: {status_color};'>{icon} {status}</span>", unsafe_allow_html=True)
                with st.expander("See error details"):
                    st.error(error_msg)
            else:
                st.progress(progress/100, text=f"{icon} {status}")

def show_bulk_loading_progress(timeframe_files: List[str], timeframes_loaded: List[str], 
                              next_timeframe_to_load: int):
    """
    Show progress of bulk loading operation
    
    Args:
        timeframe_files: List of timeframe files
        timeframes_loaded: List of loaded timeframes
        next_timeframe_to_load: Index of next timeframe to load
    """
    st.markdown("**Bulk Loading Progress:**")
    
    # Add overall progress bar
    total_tfs = len(timeframe_files) - 1  # Excluding monthly which is already loaded
    loaded_tfs = len(timeframes_loaded) - 1  # Excluding monthly
    
    if total_tfs > 0:  # Avoid division by zero
        progress_percentage = loaded_tfs / total_tfs
        st.progress(progress_percentage, text=f"Overall progress: {loaded_tfs}/{total_tfs} timeframes")
    
    # Show next timeframe being loaded
    sorted_timeframes = list(reversed(timeframe_files))
    if next_timeframe_to_load < len(sorted_timeframes):
        next_file = sorted_timeframes[next_timeframe_to_load]
        next_tf = next_file.split('.')[0]
        friendly_name = TIMEFRAME_LABELS.get(next_tf, next_tf)
        
        if next_tf != "M":  # Skip monthly as it's already loaded
            st.info(f"🔄 Currently loading: {friendly_name} ({next_tf})")

def reset_button_state(key: str):
    """
    Reset a button's state to 'ready'
    
    Args:
        key: Button key without the _state suffix
    """
    button_state_key = f"{key}_state"
    if button_state_key in st.session_state:
        st.session_state[button_state_key] = "ready"
