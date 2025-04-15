"""
Help content and explanations for the Gold Market Analysis Dashboard
"""

# Main app explanations
APP_INTRO = """
Welcome to the Gold Market Analysis Dashboard. This tool helps you analyze gold market patterns
across different timeframes. Follow these steps to get started:

1. Connect to Azure Storage 
2. Load Monthly data
3. Then load additional timeframes as needed
"""

# Help texts for different sections
DATA_LOADING_HELP = """
**Loading sequence**: Start with Monthly data, then load additional timeframes as needed.
Each timeframe will load independently and show its progress below.
"""

PROFILE_TYPES_HELP = """
Profiles allow you to analyze market behavior in different cyclical patterns:

- **Decennial**: Looks at patterns based on the last digit of the year (0-9)
- **Presidential**: Analyzes the 4-year presidential cycle pattern
- **Quarterly**: Shows seasonal patterns by quarter (Q1-Q4)
- **Monthly**: Reveals which months historically perform best/worst
- **Weekly**: Identifies patterns in specific weeks of the year
- **Week of Month**: Shows if certain weeks within a month perform better
- **Day of Week**: Analyzes which trading days perform better (Mon-Fri)
- **Trading Session**: Compares pre-market, regular, and post-market sessions

Each profile helps identify different cyclical patterns that may affect gold prices.
"""

ANALYSIS_TABS_HELP = """
The analysis is organized into three tabs:

- **Profile Analysis**: Shows probability, return and volatility statistics for the selected profile
- **Sequential Patterns**: Identifies recurring sequences in market behavior
- **Historic Barcode**: Shows a visual history of market performance as a color-coded table

These different views help identify patterns from multiple perspectives.
"""

PROFILE_ANALYSIS_HELP = """
**Profile Analysis shows how gold performs during different market cycles.**

- **Green Bars**: Probability of price closing higher (bullish)
- **Red Bars**: Probability of price closing lower (bearish)
- **Blue Line**: Average percentage return
"""

SEQUENTIAL_PATTERNS_HELP = """
**Sequential Pattern Analysis finds recurring sequences in market behavior.**

For example, a pattern like "Green → Red → Green" shows when price went up, 
then down, then up again. The most frequent patterns may help predict future movements.
"""

BARCODE_HELP = """
**The Historic Barcode view displays market movements as a color-coded table.**

- **Green Cells**: Days when price closed higher than it opened
- **Red Cells**: Days when price closed lower than it opened
- **Darker Colors**: Larger price movements
"""

# Complete user guide
USER_GUIDE = """
## Overview

This dashboard allows you to analyze gold market data across different timeframes, from 1-minute charts to monthly data.
It provides various types of analysis to help you understand market patterns and behavior.

## Key Terms

- **Timeframe**: The interval of each data point (1-minute, hourly, daily, etc.)
- **Profile**: A pattern analysis based on different time cycles
- **Return**: The percentage change in price between periods
- **Volatility**: How much the price fluctuates, measured by ATR (Average True Range)
- **Green/Red Day**: A day where the closing price is higher/lower than opening price

## Analysis Types Explained

### Profile Analysis

- **Decennial**: Analyzes patterns based on the year ending digit (0-9)
- **Presidential**: Shows market patterns across the 4-year presidential cycle
- **Quarterly**: Examines seasonal patterns by quarter
- **Monthly**: Shows how the market performs in each month
- **Weekly**: Analyzes patterns by week of the year
- **Week of Month**: Shows patterns based on which week of the month it is
- **Day of Week**: Examines patterns by day of the trading week
- **Trading Session**: Looks at pre-market, regular, and post-market performance

### Metrics Explained

- **Green Probability**: Likelihood of a price increase (close > open)
- **Red Probability**: Likelihood of a price decrease (close < open)
- **Average Return**: Mean percentage change in price
- **Return Standard Deviation**: Variability of returns
- **Average ATR**: Typical volatility level
- **ATR Category**: Volatility level categorized as low, medium, or high
"""

INTERPRETATION_GUIDE = """
### Interpreting Profile Analysis

- **High Green Probability (>60%)**: Historically bullish periods
- **High Red Probability (>60%)**: Historically bearish periods
- **High Average Return**: Periods with strong directional movement
- **High Standard Deviation**: Periods with unpredictable returns
- **High ATR**: Periods of increased volatility

### Example Analysis

If December shows a 70% green probability with a +1.2% average return, this suggests:

1. Gold has a strong tendency to rise in December
2. When it does rise, it typically gains about 1.2%
3. This pattern might be tradable if it persists across multiple years

Always verify patterns across multiple timeframes before making trading decisions.
"""

# Dictionary mapping timeframe codes to friendly names
TIMEFRAME_LABELS = {
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

# Dictionary mapping profile types to friendly labels
PROFILE_LABELS = {
    "decennial": "Decennial Cycle (Year Ending 0-9)",
    "presidential": "Presidential Cycle (Years 1-4)",
    "quarter": "Quarterly (Q1-Q4)",
    "month": "Monthly (Jan-Dec)",
    "week": "Weekly (Weeks 1-52)",
    "week_of_month": "Week of Month (1-4/5)",
    "day": "Day of Week (Mon-Fri)",
    "session": "Trading Session (Pre/Regular/Post)"
}
