# Gold Market Analysis Dashboard

![Task Banner](https://github.com/Zendata-labs/market_algo_azure/blob/main/jkkhg'.PNG)

A comprehensive Streamlit application for analyzing gold market data across multiple timeframes and profile types. This dashboard provides historical analysis of gold price movements, probabilities, returns, and volatility patterns to help identify trading opportunities.

## Features

- **Multi-timeframe Analysis**: Analyze gold data across 10 different timeframes (1-minute to monthly)
- **Profile Analysis**: Visualize gold market behavior across 8 different profile types:
  - Decennial (0-9 years of each decade)
  - Presidential Cycle (years 1-4)
  - Quarterly (Q1-Q4)
  - Monthly (Jan-Dec)
  - Weekly (52 weeks of year)
  - Week of Month (weeks 1-4)
  - Day of Week (trading days 1-5)
  - Trading Session (pre-market, regular, post-market)
- **Sequential Pattern Analysis**: Identify common sequential patterns in price movements and volatility
- **Historic "Barcode" Profile**: View your current position within each cycle
- **Interactive Visualizations**: Bar charts and line charts with hover effects for detailed information

## Data Structure

The application uses gold price data with the following columns:
- date
- open
- high
- low
- close

## Getting Started

### Prerequisites

- Python 3.7+
- Azure Blob Storage account with gold price data

### Installation

1. Clone the repository
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
3. Configure your Azure Blob Storage credentials in the `.env` file
4. Run the application:
   ```
   streamlit run main.py
   ```

## Usage Guide

1. **Select Timeframe**: Choose from 10 available timeframes in the sidebar
2. **Set Date Range**: Filter data by specific date range
3. **Select Profile Type**: Choose the type of profile analysis to view
4. **Analyze Charts**: View bar and line charts showing:
   - Green/Red probabilities
   - Average returns
   - ATR (Average True Range) categories
5. **Explore Sequential Patterns**: Identify common patterns in price movements and volatility
6. **Check Barcode Profile**: See your current position in different market cycles

## File Structure

- `main.py`: Main Streamlit application file
- `utils.py`: Utility functions for data processing and analysis
- `config.py`: Configuration settings for Azure Blob Storage
- `.env`: Environment variables for sensitive information
- `requirements.txt`: Required Python packages

## Customization

The application's visual design uses a dark theme with gold accents to match the gold market theme. The UI is designed to be intuitive for both technical and non-technical users.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
