import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from datetime import datetime, timedelta
# Import get_sequential_patterns from utils to fix the error
from utils import get_sequential_patterns, prepare_profile_data, calculate_atr, categorize_atr

# Function to create color-coded metrics
def display_metric(label, value, is_percentage=False, is_good_when_high=True):
    format_value = f"{value:.2f}%" if is_percentage else f"{value:.2f}"
    
    if value > 0:
        color_class = "green-text" if is_good_when_high else "red-text"
    elif value < 0:
        color_class = "red-text" if is_good_when_high else "green-text"
    else:
        color_class = ""
    
    st.markdown(
        f"""
        <div style="padding: 10px; border-radius: 5px; background-color: #1e2130; margin-bottom: 10px;">
            <span class="small-text">{label}</span><br>
            <span class="{color_class}">{format_value}</span>
        </div>
        """, 
        unsafe_allow_html=True
    )

# Function to create bar charts with Plotly
def create_bar_chart(data, x_col, prob_col, return_col, atr_col, title, height=400):
    # Create figure with secondary y-axis
    fig = go.Figure()
    
    # Add probability bars (green)
    fig.add_trace(go.Bar(
        x=data[x_col],
        y=data[prob_col] * 100,  # Convert to percentage
        name='Probability (%)',
        marker_color='rgba(46, 125, 50, 0.7)',
        hovertemplate='%{x}<br>Probability: %{y:.1f}%<extra></extra>'
    ))
    
    # Add average return bars (blue)
    fig.add_trace(go.Bar(
        x=data[x_col],
        y=data[return_col],
        name='Avg Return (%)',
        marker_color='rgba(33, 150, 243, 0.7)',
        hovertemplate='%{x}<br>Avg Return: %{y:.2f}%<extra></extra>',
        yaxis='y2'  # Use secondary y-axis
    ))
    
    # Add ATR markers (red dots)
    fig.add_trace(go.Scatter(
        x=data[x_col],
        y=data[atr_col],
        mode='markers',
        name='ATR Category',
        marker=dict(
            color='rgba(211, 47, 47, 0.9)',
            size=10,
            symbol='circle',
            line=dict(width=1, color='rgba(0, 0, 0, 0.5)')
        ),
        hovertemplate='%{x}<br>ATR Category: %{y:.0f}<extra></extra>',
        yaxis='y3'  # Use tertiary y-axis
    ))
    
    # Map day numbers to day names for day profile
    if x_col == 'Day of Week':
        day_names = {1: 'Mon', 2: 'Tue', 3: 'Wed', 4: 'Thu', 5: 'Fri'}
        # Update x-axis ticks
        fig.update_xaxes(
            tickvals=list(day_names.keys()),
            ticktext=list(day_names.values())
        )
    
    # Customize layout
    fig.update_layout(
        title={
            'text': title,
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'color': '#ffd700', 'size': 24}
        },
        xaxis_title=x_col,
        yaxis=dict(
            title='Probability (%)',
            titlefont=dict(color='rgba(46, 125, 50, 1)'),
            tickfont=dict(color='rgba(46, 125, 50, 1)'),
            range=[0, 100],
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.1)'
        ),
        yaxis2=dict(
            title='Average Return (%)',
            titlefont=dict(color='rgba(33, 150, 243, 1)'),
            tickfont=dict(color='rgba(33, 150, 243, 1)'),
            anchor='x',
            overlaying='y',
            side='right',
            showgrid=False
        ),
        yaxis3=dict(
            title='ATR Points',
            range=[0, 500],  # Range for ATR points (0-500 as shown in the image)
            titlefont=dict(color='rgba(211, 47, 47, 1)'),
            tickfont=dict(color='rgba(211, 47, 47, 1)'),
            anchor='free',
            overlaying='y',
            side='right',
            position=1.0,
            tickvals=[100, 200, 300, 400, 500],
            showgrid=False
        ),
        hovermode='x unified',
        plot_bgcolor='rgba(14, 17, 23, 0.8)',
        paper_bgcolor='rgba(14, 17, 23, 0)',
        legend=dict(
            orientation='h',
            y=1.1,
            x=0.5,
            xanchor='center',
            font=dict(color='white', size=14)
        ),
        height=600,
        margin=dict(l=60, r=60, t=100, b=80),
        barmode='group'
    )
    
    # Update x-axis label appearance
    fig.update_xaxes(
        tickangle=-45,
        tickfont=dict(color='white', size=14),
        title_font=dict(color='white', size=16)
    )
    
    return fig

# Function to create line charts
def create_line_chart(data, x_col, prob_col, return_col, atr_col, title, height=400):
    # Create figure with secondary y-axis
    fig = go.Figure()
    
    # Add probability line (green)
    fig.add_trace(go.Scatter(
        x=data[x_col],
        y=data[prob_col] * 100,  # Convert to percentage
        name='Probability (%)',
        line=dict(color='rgba(46, 125, 50, 0.9)', width=3),
        hovertemplate='%{x}<br>Probability: %{y:.1f}%<extra></extra>'
    ))
    
    # Add average return line (blue)
    fig.add_trace(go.Scatter(
        x=data[x_col],
        y=data[return_col],
        name='Avg Return (%)',
        line=dict(color='rgba(33, 150, 243, 0.9)', width=3),
        hovertemplate='%{x}<br>Avg Return: %{y:.2f}%<extra></extra>',
        yaxis='y2'  # Use secondary y-axis
    ))
    
    # Add ATR category line (red)
    fig.add_trace(go.Scatter(
        x=data[x_col],
        y=data[atr_col],
        name='ATR Category',
        line=dict(color='rgba(211, 47, 47, 0.9)', width=3, dash='dot'),
        mode='lines+markers',
        marker=dict(size=8),
        hovertemplate='%{x}<br>ATR Category: %{y:.0f}<extra></extra>',
        yaxis='y3'  # Use tertiary y-axis
    ))
    
    # Customize layout - similar to bar chart but adapted for line chart
    fig.update_layout(
        title={
            'text': title,
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'color': '#ffd700', 'size': 24}
        },
        xaxis_title=x_col,
        yaxis=dict(
            title='Probability (%)',
            titlefont=dict(color='rgba(46, 125, 50, 1)'),
            tickfont=dict(color='rgba(46, 125, 50, 1)'),
            range=[0, 100],
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.1)'
        ),
        yaxis2=dict(
            title='Average Return (%)',
            titlefont=dict(color='rgba(33, 150, 243, 1)'),
            tickfont=dict(color='rgba(33, 150, 243, 1)'),
            anchor='x',
            overlaying='y',
            side='right',
            showgrid=False
        ),
        yaxis3=dict(
            title='ATR Points',
            range=[0, 500],  # Range for ATR points (0-500 as shown in the image)
            titlefont=dict(color='rgba(211, 47, 47, 1)'),
            tickfont=dict(color='rgba(211, 47, 47, 1)'),
            anchor='free',
            overlaying='y',
            side='right',
            position=1.0,
            tickvals=[100, 200, 300, 400, 500],
            showgrid=False
        ),
        hovermode='x unified',
        plot_bgcolor='rgba(14, 17, 23, 0.8)',
        paper_bgcolor='rgba(14, 17, 23, 0)',
        legend=dict(
            orientation='h',
            y=1.1,
            x=0.5,
            xanchor='center',
            font=dict(color='white', size=14)
        ),
        height=600,
        margin=dict(l=60, r=60, t=100, b=80)
    )
    
    # Update x-axis label appearance
    fig.update_xaxes(
        tickangle=-45,
        tickfont=dict(color='white', size=14),
        title_font=dict(color='white', size=16)
    )
    
    return fig

# Function to display sequential patterns
def display_sequential_patterns(data, column, pattern_length=3, top_n=5):
    """
    Display sequential pattern analysis
    """
    try:
        # Check if column exists in data
        if column not in data.columns:
            # If 'is_green' not found, try to calculate it first
            if column == 'is_green' and all(col in data.columns for col in ['open', 'close']):
                data['is_green'] = data['close'] > data['open']
            else:
                st.warning(f"Column '{column}' not found in data. Cannot display sequential patterns.")
                return
        
        # Get patterns
        series = data[column]
        patterns = get_sequential_patterns(series, pattern_length)
        
        if not patterns:
            st.warning("No patterns found.")
            return
        
        # Display top patterns
        st.markdown("### Top Sequential Patterns")
        
        # Format patterns for display
        pattern_data = []
        for pattern, count in patterns[:top_n]:  # Show top n
            pattern_str = " → ".join([str(p) for p in pattern])
            pattern_data.append({
                "Pattern": pattern_str,
                "Count": count,
                "Frequency": f"{count / len(series):.1%}"
            })
            
        # Convert to DataFrame for display
        pattern_df = pd.DataFrame(pattern_data)
        st.table(pattern_df)
        
    except Exception as e:
        st.error(f"Error displaying sequential patterns: {str(e)}")
        st.exception(e)

# Function to display profile section
def display_profile(data_dict, profile_type, selected_timeframe, start_date=None, end_date=None):
    """
    Display profile section with improved visualization
    """
    from utils import prepare_profile_data, calculate_atr, categorize_atr
    
    try:
        # Get the selected data
        df = data_dict.get(selected_timeframe, pd.DataFrame())
        
        if df.empty:
            st.warning(f"No data available for {selected_timeframe}")
            return
            
        # Prepare filter parameters
        filter_params = {
            'timeframe': selected_timeframe,
            'start_date': start_date,
            'end_date': end_date
        }
        
        # Get aggregated data for selected profile
        agg_data = prepare_profile_data(df, profile_type, filter_params)
        
        if agg_data.empty:
            st.warning("Not enough data to create profile")
            return
            
        # Get the group name column (first column in the dataframe)
        group_name = agg_data.columns[0]
        
        # Add view mode selector
        view_mode = st.radio(
            "View Mode",
            ["Green/Red Probability", "Average Return", "ATR in Points"],
            horizontal=True,
            key=f"view_mode_{profile_type}_{selected_timeframe}"
        )
        
        # Map UI selection to view_mode parameter
        view_mode_param = {
            "Green/Red Probability": "probability",
            "Average Return": "return",
            "ATR in Points": "atr_points"
        }[view_mode]
        
        # Create chart using our improved function
        if profile_type == 'session':
            fig = create_session_profile_chart(agg_data, selected_timeframe, view_mode_param)
        else:
            fig = create_profile_chart(agg_data, group_name, selected_timeframe, profile_type, view_mode_param)
        
        # Display the chart
        st.plotly_chart(fig, use_container_width=True)
        
        # Display metrics table with details
        with st.expander("View Detailed Metrics"):
            # Convert data for display
            display_df = agg_data.copy()
            
            # Format probability columns
            for col in ['green_probability', 'red_probability']:
                if col in display_df.columns:
                    display_df[col] = display_df[col].apply(lambda x: f"{x:.1%}")
                    
            # Format return columns
            for col in ['avg_return', 'avg_green_return', 'avg_red_return', 'return_std']:
                if col in display_df.columns:
                    display_df[col] = display_df[col].apply(lambda x: f"{x:.2f}%")
                    
            # Rename columns for better display
            renamed_columns = {
                group_name: group_name,
                'green_probability': 'Green Prob',
                'red_probability': 'Red Prob',
                'avg_return': 'Avg Return',
                'avg_green_return': 'Avg Green Return',
                'avg_red_return': 'Avg Red Return',
                'return_std': 'Return StdDev',
                'avg_atr': 'Avg ATR',
                'most_common_atr': 'ATR Category'
            }
            
            display_df = display_df.rename(columns={col: renamed_columns.get(col, col) for col in display_df.columns})
            
            # Display the table
            st.dataframe(
                display_df, 
                use_container_width=True,
                height=400 if len(display_df) > 10 else 300
            )
            
        # Display sequential patterns
        with st.expander("View Sequential Patterns"):
            st.markdown("### Sequential Pattern Analysis")
            
            # Prepare data for sequential analysis
            filtered_df = df.copy()
            
            if start_date:
                filtered_df = filtered_df[filtered_df['date'] >= start_date]
            if end_date:
                filtered_df = filtered_df[filtered_df['date'] <= end_date]
                
            # Create three columns for different pattern types
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("#### Green/Red Probability Patterns")
                # Calculate is_green for pattern analysis
                if 'is_green' not in filtered_df.columns and all(col in filtered_df.columns for col in ['open', 'close']):
                    filtered_df['is_green'] = filtered_df['close'] > filtered_df['open']
                    
                # Display patterns
                if 'is_green' in filtered_df.columns:
                    display_sequential_patterns(filtered_df, 'is_green', pattern_length=3)
                else:
                    st.info("Missing required columns for Green/Red patterns")
                    
            with col2:
                st.markdown("#### ATR Category Patterns")
                # Calculate ATR for pattern analysis
                if 'atr_category' not in filtered_df.columns:
                    try:
                        atr_values = calculate_atr(filtered_df)
                        filtered_df['atr'] = atr_values
                        filtered_df['atr_category'] = categorize_atr(atr_values)
                        display_sequential_patterns(filtered_df, 'atr_category', pattern_length=3)
                    except Exception as e:
                        st.error(f"Error calculating ATR patterns: {str(e)}")
                else:
                    display_sequential_patterns(filtered_df, 'atr_category', pattern_length=3)
                    
            with col3:
                st.markdown("#### Return Patterns")
                # Calculate returns for pattern analysis
                if 'return' not in filtered_df.columns and 'close' in filtered_df.columns:
                    filtered_df['return'] = filtered_df['close'].pct_change() * 100
                    
                # Create return direction series
                if 'return' in filtered_df.columns:
                    return_direction = filtered_df['return'].apply(lambda x: 'Up' if x > 0 else 'Down')
                    filter_series = pd.Series(return_direction.values, index=return_direction.index)
                    
                    # Get patterns from the series
                    patterns = get_sequential_patterns(filter_series, pattern_length=3)
                    
                    # Create a DataFrame for display
                    pattern_data = []
                    for pattern, count in patterns[:5]:
                        pattern_str = " → ".join([str(p) for p in pattern])
                        pattern_data.append({
                            "Pattern": pattern_str,
                            "Count": count,
                            "Frequency": f"{count / (len(filter_series) - 2):.1%}"
                        })
                        
                    if pattern_data:
                        pattern_df = pd.DataFrame(pattern_data)
                        st.table(pattern_df)
                    else:
                        st.info("Not enough data for Return patterns")
                else:
                    st.info("Missing required columns for Return patterns")
    
    except Exception as e:
        st.error(f"Error displaying profile: {str(e)}")
        st.exception(e)

# Historic "Barcode" Profile Table
def display_barcode_table(data_dict, timeframe, date):
    st.markdown("<h3>Historic 'Barcode' Profile Table</h3>", unsafe_allow_html=True)
    
    # Get current values for each profile type
    df = data_dict.get(timeframe, pd.DataFrame())
    
    if df.empty:
        st.warning(f"No data available for {timeframe} timeframe")
        return
    
    # Find the closest date in the dataframe to the selected date
    df['date'] = pd.to_datetime(df['date'])
    closest_date_idx = (df['date'] - pd.to_datetime(date)).abs().idxmin()
    target_date = df.loc[closest_date_idx, 'date']
    
    # Create a table with current profile positions
    profiles = [
        {'name': 'Decennial', 'total': 10, 'current': target_date.year % 10},
        {'name': 'Presidential', 'total': 4, 'current': ((target_date.year - 1) % 4) + 1},
        {'name': 'Quarter', 'total': 4, 'current': target_date.quarter},
        {'name': 'Month', 'total': 12, 'current': target_date.month},
        {'name': 'Week of Month', 'total': 4, 'current': np.ceil(target_date.day / 7).astype(int)},
        {'name': 'Week of Year', 'total': 52, 'current': target_date.isocalendar()[1]},
        {'name': 'Day of Week', 'total': 5, 'current': min(target_date.dayofweek + 1, 5)},
        {'name': 'Session', 'total': 3, 'current': 1}  # Default to regular session
    ]
    
    # Create a table-like display for the barcode
    for profile in profiles:
        # Calculate percentage for position indicator
        position_pct = (profile['current'] - 1) / profile['total'] * 100
        
        st.markdown(
            f"""
            <div style="padding: 10px; border-radius: 5px; background-color: #1e2130; margin-bottom: 10px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                    <span>{profile['name']}</span>
                    <span class="gold-accent">{profile['current']} of {profile['total']}</span>
                </div>
                <div style="background-color: #333; height: 20px; border-radius: 10px; position: relative;">
                    <div style="position: absolute; left: {position_pct}%; top: 0; width: 4px; height: 20px; background-color: #ffd700; transform: translateX(-50%);"></div>
                </div>
            </div>
            """, 
            unsafe_allow_html=True
        )

# Function to create profile chart
def create_profile_chart(agg_data, group_name, selected_timeframe, profile_type, view_mode="probability"):
    """
    Create a bar chart with probabilities and a line for average return
    
    Args:
        agg_data: DataFrame with aggregated data
        group_name: Column name for x-axis grouping
        selected_timeframe: Current timeframe (e.g. "M", "D")
        profile_type: Type of profile (e.g. "decennial", "month")
        view_mode: What to display - "probability", "return", or "atr_points"
    """
    # Define colors
    green_color = 'rgba(46, 125, 50, 0.7)'
    red_color = 'rgba(211, 47, 47, 0.7)'
    blue_color = 'rgba(33, 150, 243, 0.7)'
    gold_color = '#ffd700'
    text_color = '#ffffff'
    
    # Create a figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    if view_mode == "probability":
        # Add bars for green probability
        fig.add_trace(
            go.Bar(
                x=agg_data[group_name],
                y=agg_data['green_probability'],
                name='Green Probability',
                marker_color=green_color,
                opacity=0.9,
                text=[f"{p:.1%}" for p in agg_data['green_probability']],
                textposition="inside",
                textfont=dict(color='white', size=12),
                width=0.4,
                offset=-0.25,
                hovertemplate='Green Prob: %{text}<extra></extra>'
            ),
            secondary_y=False
        )
        
        # Add bars for red probability
        fig.add_trace(
            go.Bar(
                x=agg_data[group_name],
                y=agg_data['red_probability'],
                name='Red Probability',
                marker_color=red_color,
                opacity=0.9,
                text=[f"{p:.1%}" for p in agg_data['red_probability']],
                textposition="inside",
                textfont=dict(color='white', size=12),
                width=0.4,
                offset=0.25,
                hovertemplate='Red Prob: %{text}<extra></extra>'
            ),
            secondary_y=False
        )
        
        # Add line for average return with dots
        fig.add_trace(
            go.Scatter(
                x=agg_data[group_name],
                y=agg_data['avg_return'],
                name='Average Return',
                mode='lines+markers',
                line=dict(color=blue_color, width=3),
                marker=dict(size=8, color=blue_color, symbol='circle'),
                text=[f"{r:.2f}%" for r in agg_data['avg_return']],
                hovertemplate='Return: %{text}<extra></extra>'
            ),
            secondary_y=True
        )
        
        # Set y-axis titles based on mode
        y_axis_title = "Probability"
        y_axis2_title = "Average Return (%)"
        
    elif view_mode == "return":
        # For return mode, focus on green/red returns
        if 'avg_green_return' in agg_data.columns and 'avg_red_return' in agg_data.columns:
            fig.add_trace(
                go.Bar(
                    x=agg_data[group_name],
                    y=agg_data['avg_green_return'],
                    name='Green Return',
                    marker_color=green_color,
                    opacity=0.9,
                    text=[f"{r:.2f}%" for r in agg_data['avg_green_return']],
                    textposition="inside",
                    textfont=dict(color='white', size=12),
                    width=0.4,
                    offset=-0.25,
                    hovertemplate='Green Return: %{text}<extra></extra>'
                ),
                secondary_y=False
            )
            
            fig.add_trace(
                go.Bar(
                    x=agg_data[group_name],
                    y=agg_data['avg_red_return'],
                    name='Red Return',
                    marker_color=red_color,
                    opacity=0.9,
                    text=[f"{r:.2f}%" for r in agg_data['avg_red_return']],
                    textposition="inside",
                    textfont=dict(color='white', size=12),
                    width=0.4,
                    offset=0.25,
                    hovertemplate='Red Return: %{text}<extra></extra>'
                ),
                secondary_y=False
            )
            
            # Add standard deviation line
            if 'return_std' in agg_data.columns:
                fig.add_trace(
                    go.Scatter(
                        x=agg_data[group_name],
                        y=agg_data['return_std'],
                        name='Return StdDev',
                        mode='lines+markers',
                        line=dict(color=blue_color, width=3),
                        marker=dict(size=8, color=blue_color, symbol='circle'),
                        text=[f"{r:.2f}%" for r in agg_data['return_std']],
                        hovertemplate='StdDev: %{text}<extra></extra>'
                    ),
                    secondary_y=True
                )
        else:
            # Fallback if specific return columns aren't available
            fig.add_trace(
                go.Bar(
                    x=agg_data[group_name],
                    y=agg_data['avg_return'],
                    name='Average Return',
                    marker_color=blue_color,
                    opacity=0.9,
                    text=[f"{r:.2f}%" for r in agg_data['avg_return']],
                    textposition="inside",
                    textfont=dict(color='white', size=12),
                    hovertemplate='Return: %{text}<extra></extra>'
                ),
                secondary_y=False
            )
        
        # Set y-axis titles based on mode
        y_axis_title = "Return (%)"
        y_axis2_title = "Return StdDev (%)"
        
    elif view_mode == "atr_points":
        # ATR points view - showing ATR categories as points (1, 2, 3)
        if 'most_common_atr' in agg_data.columns:
            # Convert ATR categories to numeric if they're not already
            numeric_atr = agg_data['most_common_atr']
            if not pd.api.types.is_numeric_dtype(numeric_atr):
                # Handle non-numeric case - try to convert or use mapping
                try:
                    numeric_atr = pd.to_numeric(numeric_atr)
                except:
                    # Use a mapping if conversion fails
                    atr_mapping = {'Low': 1, 'Average': 2, 'High': 3}
                    numeric_atr = numeric_atr.map(lambda x: atr_mapping.get(x, x))
            
            # Create a new column for the chart
            agg_data['atr_points'] = numeric_atr
            
            # Colors for ATR points (1=green, 2=yellow, 3=red)
            atr_colors = {
                1: 'rgba(46, 125, 50, 0.7)',  # Low volatility - green
                2: 'rgba(255, 193, 7, 0.7)',  # Medium volatility - amber
                3: 'rgba(211, 47, 47, 0.7)'   # High volatility - red
            }
            
            # Create bars with colors based on ATR level
            for atr_level in [1, 2, 3]:
                # Filter data for this ATR level
                mask = agg_data['atr_points'] == atr_level
                if mask.any():
                    label = {1: 'Low', 2: 'Average', 3: 'High'}.get(atr_level, f'Level {atr_level}')
                    fig.add_trace(
                        go.Bar(
                            x=agg_data.loc[mask, group_name],
                            y=agg_data.loc[mask, 'atr_points'],
                            name=f'ATR: {label}',
                            marker_color=atr_colors.get(atr_level, 'gray'),
                            opacity=0.9,
                            text=[f"{label} ({int(val)})" for val in agg_data.loc[mask, 'atr_points']],
                            textposition="inside",
                            textfont=dict(color='white', size=12),
                            hovertemplate=f'ATR: {label} (Level {atr_level})<extra></extra>'
                        ),
                        secondary_y=False
                    )
            
            # Add the actual ATR value as a line if available
            if 'avg_atr' in agg_data.columns:
                fig.add_trace(
                    go.Scatter(
                        x=agg_data[group_name],
                        y=agg_data['avg_atr'],
                        name='Average ATR',
                        mode='lines+markers',
                        line=dict(color=blue_color, width=3),
                        marker=dict(size=8, color=blue_color, symbol='circle'),
                        text=[f"{r:.2f}" for r in agg_data['avg_atr']],
                        hovertemplate='ATR Value: %{text}<extra></extra>'
                    ),
                    secondary_y=True
                )
        else:
            # Fallback if ATR categories aren't available
            if 'avg_atr' in agg_data.columns:
                fig.add_trace(
                    go.Bar(
                        x=agg_data[group_name],
                        y=agg_data['avg_atr'],
                        name='Average ATR',
                        marker_color=blue_color,
                        opacity=0.9,
                        text=[f"{r:.2f}" for r in agg_data['avg_atr']],
                        textposition="inside",
                        textfont=dict(color='white', size=12),
                        hovertemplate='ATR: %{text}<extra></extra>'
                    ),
                    secondary_y=False
                )
        
        # Set y-axis titles based on mode
        y_axis_title = "ATR Points (1=Low, 2=Avg, 3=High)"
        y_axis2_title = "Average ATR Value"
    
    # Create a descriptive title
    timeframe_labels = {
        "1min": "1-minute",
        "5min": "5-minute",
        "10min": "10-minute", 
        "15min": "15-minute",
        "30min": "30-minute",
        "1h": "1-hour",
        "4h": "4-hour",
        "D": "Daily",
        "W": "Weekly",
        "M": "Monthly"
    }
    
    profile_labels = {
        "decennial": "Decennial Cycle",
        "presidential": "Presidential Cycle",
        "quarter": "Quarterly",
        "month": "Monthly",
        "week": "Weekly",
        "week_of_month": "Week of Month",
        "day": "Day of Week",
        "session": "Trading Session"
    }
    
    view_labels = {
        "probability": "Probability Analysis",
        "return": "Return Analysis",
        "atr_points": "ATR Points Analysis"
    }
    
    friendly_timeframe = timeframe_labels.get(selected_timeframe, selected_timeframe)
    friendly_profile = profile_labels.get(profile_type, profile_type.capitalize())
    friendly_view = view_labels.get(view_mode, view_mode.capitalize())
    
    # Update layout
    fig.update_layout(
        title={
            'text': f"{friendly_profile} - {friendly_view} - {friendly_timeframe} Data",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(size=24, color=gold_color)
        },
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(size=14, color=text_color)
        ),
        barmode='group',
        height=600,  # Make chart taller
        margin=dict(l=60, r=60, t=100, b=80),  # Increase margins
        plot_bgcolor='#1f1f1f',
        paper_bgcolor='#1f1f1f',
        font=dict(color=text_color, size=14),  # Increase default font size
        xaxis=dict(
            title=dict(text=group_name, font=dict(size=16, color=text_color)),  # Larger x-axis title
            tickangle=-45 if profile_type in ["month", "week", "decennial"] else 0,  # Angle labels for certain profiles
            tickfont=dict(size=14, color=text_color),  # Larger tick labels
            gridcolor='#333',
            tickmode='auto',
            nticks=15 if len(agg_data) > 12 else len(agg_data),  # Control number of ticks
        ),
        yaxis=dict(
            title=dict(text=y_axis_title, font=dict(size=16, color=text_color)),  # Larger y-axis title
            gridcolor='#333',
            tickfont=dict(size=14, color=text_color)  # Larger tick labels
        ),
        yaxis2=dict(
            title=dict(text=y_axis2_title, font=dict(size=16, color=text_color)),  # Larger secondary y-axis title
            gridcolor='#333',
            tickfont=dict(size=14, color=text_color)  # Larger tick labels
        )
    )
    
    # Format y-axis based on view mode
    if view_mode == "probability":
        fig.update_yaxes(tickformat='.0%', range=[0, 1], secondary_y=False)
    elif view_mode == "return":
        fig.update_yaxes(tickformat='.2f', secondary_y=False)
        fig.update_yaxes(tickformat='.2f', secondary_y=True)
    elif view_mode == "atr_points":
        fig.update_yaxes(range=[0.5, 3.5], dtick=1, secondary_y=False)
    
    # Add a subtle gold-colored border around the plot
    fig.update_layout(
        shapes=[
            dict(
                type='rect',
                xref='paper',
                yref='paper',
                x0=0,
                y0=0,
                x1=1,
                y1=1,
                line=dict(
                    color=gold_color,
                    width=2,
                ),
                opacity=0.3
            )
        ]
    )
    
    return fig

# Function to create session profile chart
def create_session_profile_chart(agg_data, selected_timeframe, view_mode="probability"):
    """
    Create a specialized chart for session profiles that shows the 3 trading sessions in distinct parts
    
    Args:
        agg_data: DataFrame with aggregated session data
        selected_timeframe: Current timeframe
        view_mode: What to display - "probability", "return", or "atr_points"
    """
    # Define colors
    green_color = 'rgba(46, 125, 50, 0.7)'
    red_color = 'rgba(211, 47, 47, 0.7)'
    blue_color = 'rgba(33, 150, 243, 0.7)'
    gold_color = '#ffd700'
    text_color = '#ffffff'
    
    session_labels = ['Pre-Market', 'Regular Hours', 'Post-Market']
    
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Prepare data
    if view_mode == "probability":
        # Create grouped bar chart for probabilities
        for i, session in enumerate([0, 1, 2]):
            session_data = agg_data[agg_data['Trading Session'] == session]
            if not session_data.empty:
                # Green probability bars
                fig.add_trace(
                    go.Bar(
                        x=[session_labels[i]],
                        y=[session_data['green_probability'].values[0]],
                        name=f'{session_labels[i]} Green',
                        marker_color=green_color,
                        opacity=0.9,
                        text=[f"{session_data['green_probability'].values[0]:.1%}"],
                        textposition="inside",
                        textfont=dict(color='white', size=12),
                        width=0.4,
                        offset=-0.25,
                        hovertemplate=f'{session_labels[i]} Green: %{{text}}<extra></extra>'
                    ),
                    secondary_y=False
                )
                
                # Red probability bars
                fig.add_trace(
                    go.Bar(
                        x=[session_labels[i]],
                        y=[session_data['red_probability'].values[0]],
                        name=f'{session_labels[i]} Red',
                        marker_color=red_color,
                        opacity=0.9,
                        text=[f"{session_data['red_probability'].values[0]:.1%}"],
                        textposition="inside",
                        textfont=dict(color='white', size=12),
                        width=0.4,
                        offset=0.25,
                        hovertemplate=f'{session_labels[i]} Red: %{{text}}<extra></extra>'
                    ),
                    secondary_y=False
                )
                
                # Average return marker
                fig.add_trace(
                    go.Scatter(
                        x=[session_labels[i]],
                        y=[session_data['avg_return'].values[0]],
                        name=f'{session_labels[i]} Return',
                        mode='markers',
                        marker=dict(size=12, color=blue_color, symbol='diamond'),
                        text=[f"{session_data['avg_return'].values[0]:.2f}%"],
                        hovertemplate=f'{session_labels[i]} Return: %{{text}}<extra></extra>'
                    ),
                    secondary_y=True
                )
                
        # Connect returns with a line
        returns = []
        for i, session in enumerate([0, 1, 2]):
            session_data = agg_data[agg_data['Trading Session'] == session]
            if not session_data.empty:
                returns.append(session_data['avg_return'].values[0])
            else:
                returns.append(None)
                
        # Add connecting line if we have enough points
        valid_returns = [r for r in returns if r is not None]
        if len(valid_returns) > 1:
            fig.add_trace(
                go.Scatter(
                    x=session_labels,
                    y=returns,
                    name='Return Trend',
                    mode='lines',
                    line=dict(color=blue_color, width=2, dash='dot'),
                    hoverinfo='skip'
                ),
                secondary_y=True
            )
        
        # Set y-axis titles
        y_axis_title = "Probability"
        y_axis2_title = "Average Return (%)"
        
    elif view_mode == "return":
        # Returns mode - focus on green/red returns
        for i, session in enumerate([0, 1, 2]):
            session_data = agg_data[agg_data['Trading Session'] == session]
            if not session_data.empty:
                # Green return bars
                if 'avg_green_return' in session_data.columns:
                    fig.add_trace(
                        go.Bar(
                            x=[session_labels[i]],
                            y=[session_data['avg_green_return'].values[0]],
                            name=f'{session_labels[i]} Green Return',
                            marker_color=green_color,
                            opacity=0.9,
                            text=[f"{session_data['avg_green_return'].values[0]:.2f}%"],
                            textposition="inside",
                            textfont=dict(color='white', size=12),
                            width=0.4,
                            offset=-0.25,
                            hovertemplate=f'{session_labels[i]} Green Return: %{{text}}<extra></extra>'
                        ),
                        secondary_y=False
                    )
                
                # Red return bars
                if 'avg_red_return' in session_data.columns:
                    fig.add_trace(
                        go.Bar(
                            x=[session_labels[i]],
                            y=[session_data['avg_red_return'].values[0]],
                            name=f'{session_labels[i]} Red Return',
                            marker_color=red_color,
                            opacity=0.9,
                            text=[f"{session_data['avg_red_return'].values[0]:.2f}%"],
                            textposition="inside",
                            textfont=dict(color='white', size=12),
                            width=0.4,
                            offset=0.25,
                            hovertemplate=f'{session_labels[i]} Red Return: %{{text}}<extra></extra>'
                        ),
                        secondary_y=False
                    )
                
                # Return std marker
                if 'return_std' in session_data.columns:
                    fig.add_trace(
                        go.Scatter(
                            x=[session_labels[i]],
                            y=[session_data['return_std'].values[0]],
                            name=f'{session_labels[i]} StdDev',
                            mode='markers',
                            marker=dict(size=12, color=blue_color, symbol='diamond'),
                            text=[f"{session_data['return_std'].values[0]:.2f}%"],
                            hovertemplate=f'{session_labels[i]} StdDev: %{{text}}<extra></extra>'
                        ),
                        secondary_y=True
                    )
        
        # Connect StdDev with a line
        stds = []
        for i, session in enumerate([0, 1, 2]):
            session_data = agg_data[agg_data['Trading Session'] == session]
            if not session_data.empty and 'return_std' in session_data.columns:
                stds.append(session_data['return_std'].values[0])
            else:
                stds.append(None)
                
        # Add connecting line if we have enough points
        valid_stds = [s for s in stds if s is not None]
        if len(valid_stds) > 1:
            fig.add_trace(
                go.Scatter(
                    x=session_labels,
                    y=stds,
                    name='StdDev Trend',
                    mode='lines',
                    line=dict(color=blue_color, width=2, dash='dot'),
                    hoverinfo='skip'
                ),
                secondary_y=True
            )
        
        # Set y-axis titles
        y_axis_title = "Return (%)"
        y_axis2_title = "Return StdDev (%)"
        
    elif view_mode == "atr_points":
        # ATR points mode
        for i, session in enumerate([0, 1, 2]):
            session_data = agg_data[agg_data['Trading Session'] == session]
            if not session_data.empty and 'most_common_atr' in session_data.columns:
                # Convert ATR category to numeric
                try:
                    atr_level = pd.to_numeric(session_data['most_common_atr'].values[0])
                except:
                    # Try to map category to numeric
                    atr_mapping = {'Low': 1, 'Average': 2, 'High': 3}
                    atr_level = atr_mapping.get(session_data['most_common_atr'].values[0], 2)
                
                # Colors for ATR levels
                atr_colors = {
                    1: 'rgba(46, 125, 50, 0.7)',  # Low volatility - green
                    2: 'rgba(255, 193, 7, 0.7)',  # Medium volatility - amber
                    3: 'rgba(211, 47, 47, 0.7)'   # High volatility - red
                }
                
                # Labels for ATR levels
                atr_labels = {1: 'Low', 2: 'Average', 3: 'High'}
                
                # Add ATR level bar
                fig.add_trace(
                    go.Bar(
                        x=[session_labels[i]],
                        y=[atr_level],
                        name=f'{session_labels[i]} ATR',
                        marker_color=atr_colors.get(atr_level, 'gray'),
                        opacity=0.9,
                        text=[f"{atr_labels.get(atr_level, 'Unknown')} ({atr_level})"],
                        textposition="inside",
                        textfont=dict(color='white', size=12),
                        hovertemplate=f'{session_labels[i]} ATR: %{{text}}<extra></extra>'
                    ),
                    secondary_y=False
                )
                
                # Add actual ATR value
                if 'avg_atr' in session_data.columns:
                    fig.add_trace(
                        go.Scatter(
                            x=[session_labels[i]],
                            y=[session_data['avg_atr'].values[0]],
                            name=f'{session_labels[i]} ATR Value',
                            mode='markers',
                            marker=dict(size=12, color=blue_color, symbol='diamond'),
                            text=[f"{session_data['avg_atr'].values[0]:.2f}"],
                            hovertemplate=f'{session_labels[i]} ATR Value: %{{text}}<extra></extra>'
                        ),
                        secondary_y=True
                    )
        
        # Connect ATR values with a line
        atrs = []
        for i, session in enumerate([0, 1, 2]):
            session_data = agg_data[agg_data['Trading Session'] == session]
            if not session_data.empty and 'avg_atr' in session_data.columns:
                atrs.append(session_data['avg_atr'].values[0])
            else:
                atrs.append(None)
                
        # Add connecting line if we have enough points
        valid_atrs = [a for a in atrs if a is not None]
        if len(valid_atrs) > 1:
            fig.add_trace(
                go.Scatter(
                    x=session_labels,
                    y=atrs,
                    name='ATR Trend',
                    mode='lines',
                    line=dict(color=blue_color, width=2, dash='dot'),
                    hoverinfo='skip'
                ),
                secondary_y=True
            )
        
        # Set y-axis titles
        y_axis_title = "ATR Points (1=Low, 2=Avg, 3=High)"
        y_axis2_title = "Average ATR Value"
    
    # Update layout
    fig.update_layout(
        title={
            'text': f"Trading Session Profile - {view_mode.replace('_', ' ').title()} Analysis",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(size=24, color=gold_color)
        },
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(size=14, color=text_color)
        ),
        barmode='group',
        height=600,  # Make chart taller
        margin=dict(l=60, r=60, t=100, b=80),  # Increase margins
        plot_bgcolor='#1f1f1f',
        paper_bgcolor='#1f1f1f',
        font=dict(color=text_color, size=14),  # Increase default font size
        xaxis=dict(
            title=dict(text='Trading Session', font=dict(size=16, color=text_color)),
            tickfont=dict(size=14, color=text_color),
            gridcolor='#333'
        ),
        yaxis=dict(
            title=dict(text=y_axis_title, font=dict(size=16, color=text_color)),
            gridcolor='#333',
            tickfont=dict(size=14, color=text_color)
        ),
        yaxis2=dict(
            title=dict(text=y_axis2_title, font=dict(size=16, color=text_color)),
            gridcolor='#333',
            tickfont=dict(size=14, color=text_color)
        )
    )
    
    # Format y-axis based on view mode
    if view_mode == "probability":
        fig.update_yaxes(tickformat='.0%', range=[0, 1], secondary_y=False)
    elif view_mode == "return":
        fig.update_yaxes(tickformat='.2f', secondary_y=False)
        fig.update_yaxes(tickformat='.2f', secondary_y=True)
    elif view_mode == "atr_points":
        fig.update_yaxes(range=[0.5, 3.5], dtick=1, secondary_y=False)
    
    # Add a subtle gold-colored border around the plot
    fig.update_layout(
        shapes=[
            dict(
                type='rect',
                xref='paper',
                yref='paper',
                x0=0,
                y0=0,
                x1=1,
                y1=1,
                line=dict(
                    color=gold_color,
                    width=2,
                ),
                opacity=0.3
            )
        ]
    )
    
    return fig

# Apply custom CSS for styling
def apply_styling():
    # Custom CSS for styling
    st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1e2130;
        border-radius: 4px 4px 0px 0px;
        padding: 10px 20px;
        color: white;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2e7d32 !important;
        color: white !important;
    }
    h1, h2, h3 {
        color: #ffd700;
    }
    .stSidebar {
        background-color: #1e2130;
    }
    .card {
        background-color: #1e2130;
        border-radius: 5px;
        padding: 20px;
        margin-bottom: 15px;
        border-left: 5px solid #ffd700;
    }
    .green-text {
        color: #2e7d32 !important;
        font-weight: bold;
    }
    .red-text {
        color: #d32f2f !important;
        font-weight: bold;
    }
    .gold-accent {
        color: #ffd700;
    }
    .small-text {
        font-size: 12px;
        color: #b0b0b0;
    }
    .stApp {
        background: linear-gradient(to bottom right, #1e1e1e, #2d2d2d, #1e1e1e);
        background-attachment: fixed;
    }
    </style>
    """, unsafe_allow_html=True)

# Create header with gold logo/title
def create_header():
    col1, col2 = st.columns([1, 6])
    with col1:
        st.markdown("# 📈")
    with col2:
        st.markdown("# Gold Market Analysis")

    st.markdown(
        """
        <div class="card">
        <p>Comprehensive analysis and visualization of Gold market data across multiple timeframes and profiles.
        This dashboard provides probabilities, returns, and volatility patterns to help identify trading opportunities.</p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    st.markdown("<br>", unsafe_allow_html=True)
