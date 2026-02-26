"""
Configuration file for Trading Bot
Customize all parameters here
"""

# ===== TRADING PARAMETERS =====
TICKERS = ['MNQ']  # Start with Micro Nasdaq

# Risk Management
RISK_REWARD_RATIO = 2.0  # 2:1 reward to risk
POSITION_SIZE = 1  # Number of contracts per trade
MAX_DAILY_TRADES = 3  # Maximum trades per day per ticker
MAX_DAILY_LOSS = 500  # Stop trading after this loss per day
ACCOUNT_RISK_PER_TRADE = 0.01  # Risk 1% of account per trade

# ===== STRATEGY PARAMETERS =====

# Market Hours (times in ET - adjust for your timezone)
PREMARKET_START_HOUR = 4
PREMARKET_START_MINUTE = 0
PREMARKET_END_HOUR = 9
PREMARKET_END_MINUTE = 30
MARKET_CLOSE_HOUR = 16
MARKET_CLOSE_MINUTE = 0

# Breakout Detection
BREAKOUT_BUFFER = 0.0001  # 0.01% buffer to confirm breakout
RETEST_TOLERANCE = 0.002  # 0.2% tolerance for retest detection

# Volume Analysis
VOLUME_LOOKBACK_PERIODS = 20  # Bars to calculate average volume
STRONG_VOLUME_THRESHOLD = 1.5  # 1.5x average volume for breakout
LESSER_VOLUME_THRESHOLD = 0.7  # 70% of breakout volume for retest

# Stop Loss
STOP_LOSS_BUFFER = 0.001  # 0.1% buffer beyond premarket level

# ===== BROKER SETTINGS =====

# Use built-in paper trading (FREE!)
BROKER_TYPE = 'paper'

# ===== DATA SETTINGS =====

# Data source: 'sample' for testing
DATA_SOURCE = 'sample'

# Data timeframe (in minutes)
TIMEFRAME = 5  # 5-minute bars

# ===== LOGGING SETTINGS =====

LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR
LOG_TO_CONSOLE = True

# ===== BACKTESTING SETTINGS =====

BACKTEST_INITIAL_CAPITAL = 100000


def validate_config():
    """Validate configuration settings"""
    errors = []
    
    if RISK_REWARD_RATIO < 1.0:
        errors.append("Risk-reward ratio should be at least 1:1")
    
    if MAX_DAILY_LOSS <= 0:
        errors.append("Max daily loss must be positive")
    
    if errors:
        print("Configuration Errors:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    return True


if __name__ == "__main__":
    if validate_config():
        print("✓ Configuration validated successfully")
        print(f"\nSettings:")
        print(f"  Tickers: {', '.join(TICKERS)}")
        print(f"  Risk-Reward: {RISK_REWARD_RATIO}:1")
        print(f"  Broker: {BROKER_TYPE}")
        print(f"  Data Source: {DATA_SOURCE}")
    else:
        print("\n✗ Please fix configuration errors")