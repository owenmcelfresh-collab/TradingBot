#!/usr/bin/env python3
"""
Main Script - Run the Trading Bot
"""

import sys
import logging
from datetime import datetime

from trading_bot import TradingBot
from backtesting import Backtester, DataProvider
import config


def setup_logging():
    """Setup logging"""
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)


def run_backtest(logger):
    """Run a backtest"""
    logger.info("="*70)
    logger.info("BACKTEST MODE")
    logger.info("="*70)
    
    # Create bot
    bot = TradingBot(tickers=config.TICKERS, risk_reward=config.RISK_REWARD_RATIO)
    
    # Generate sample data
    logger.info("Generating sample data...")
    data = {}
    for ticker in config.TICKERS:
        data[ticker] = DataProvider.create_sample_data(ticker, days=30)
    
    # Run backtest
    backtester = Backtester(bot)
    results = backtester.run(data, initial_capital=config.BACKTEST_INITIAL_CAPITAL)
    
    # Show results
    backtester.print_summary(results)
    
    logger.info("Backtest complete!")


def main():
    """Main entry point"""
    
    # Setup logging
    logger = setup_logging()
    
    # Show banner
    print("\n" + "="*70)
    print("AUTOMATED TRADING BOT")
    print("Premarket Breakout Strategy")
    print("="*70 + "\n")
    
    # Validate config
    if not config.validate_config():
        logger.error("Configuration invalid!")
        sys.exit(1)
    
    # Run backtest
    try:
        run_backtest(logger)
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
