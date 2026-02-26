"""
Backtesting Framework
Test your strategy on historical data
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict
import logging

from trading_bot import TradingBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataProvider:
    """Generate sample data for testing"""
    
    @staticmethod
    def create_sample_data(ticker: str, days: int = 30) -> pd.DataFrame:
        """
        Create realistic sample trading data
        
        Args:
            ticker: Symbol (e.g., 'MNQ')
            days: Number of days to generate
            
        Returns:
            DataFrame with OHLCV data
        """
        logger.info(f"Generating {days} days of sample data for {ticker}")
        
        np.random.seed(42)
        data = []
        
        # Base prices for different tickers
        base_price = {'MNQ': 16000, 'MES': 4800, 'NQ': 16000, 'ES': 4800}.get(ticker, 100)
        
        start_date = datetime.now() - timedelta(days=days)
        
        for day in range(days):
            current_date = start_date + timedelta(days=day)
            
            # Skip weekends
            if current_date.weekday() >= 5:
                continue
            
            # Generate premarket data (4:00 AM - 9:30 AM)
            premarket_start = current_date.replace(hour=4, minute=0, second=0)
            
            for minute in range(0, 330, 5):  # 5-minute bars
                timestamp = premarket_start + timedelta(minutes=minute)
                
                # Simulate price movement
                price = base_price + np.random.randn() * 10
                
                data.append({
                    'timestamp': timestamp,
                    'open': price + np.random.uniform(-1, 1),
                    'high': price + abs(np.random.uniform(0, 2)),
                    'low': price - abs(np.random.uniform(0, 2)),
                    'close': price,
                    'volume': np.random.randint(1000, 5000)
                })
            
            # Generate market hours (9:30 AM - 4:00 PM)
            market_start = current_date.replace(hour=9, minute=30, second=0)
            
            for minute in range(0, 390, 5):  # 6.5 hours
                timestamp = market_start + timedelta(minutes=minute)
                
                price = base_price + np.random.randn() * 15
                volume = np.random.randint(3000, 8000)
                
                data.append({
                    'timestamp': timestamp,
                    'open': price + np.random.uniform(-1, 1),
                    'high': price + abs(np.random.uniform(0, 3)),
                    'low': price - abs(np.random.uniform(0, 3)),
                    'close': price,
                    'volume': volume
                })
        
        df = pd.DataFrame(data)
        df['ticker'] = ticker
        logger.info(f"✓ Generated {len(df)} bars for {ticker}")
        return df


class Backtester:
    """Run backtests on historical data"""
    
    def __init__(self, bot: TradingBot):
        self.bot = bot
    
    def run(self, data: Dict[str, pd.DataFrame], initial_capital: float = 100000):
        """
        Run backtest
        
        Args:
            data: Dictionary of {ticker: DataFrame}
            initial_capital: Starting capital
            
        Returns:
            Results dictionary
        """
        logger.info("Starting backtest...")
        logger.info(f"Initial Capital: ${initial_capital:,.2f}")
        
        capital = initial_capital
        
        # Get all dates
        all_dates = set()
        for ticker_data in data.values():
            all_dates.update(ticker_data['timestamp'].dt.date.unique())
        all_dates = sorted(all_dates)
        
        logger.info(f"Testing {len(all_dates)} trading days")
        
        # Process each day
        for date in all_dates:
            logger.info(f"Processing {date}")
            
            # Update premarket levels
            for ticker, ticker_data in data.items():
                day_data = ticker_data[ticker_data['timestamp'].dt.date == date]
                if len(day_data) > 0:
                    self.bot.update_premarket_levels(ticker, day_data)
            
            # Process bars
            for ticker, ticker_data in data.items():
                day_data = ticker_data[ticker_data['timestamp'].dt.date == date]
                
                for idx, row in day_data.iterrows():
                    bar = row.to_dict()
                    self.bot.process_bar(ticker, bar)
        
        # Calculate results
        results = {
            'initial_capital': initial_capital,
            'final_capital': capital,
            'total_trades': len(self.bot.completed_trades)
        }
        
        return results
    
    def print_summary(self, results: Dict):
        """Print backtest results"""
        print("\n" + "="*70)
        print("BACKTEST RESULTS")
        print("="*70)
        print(f"Initial Capital: ${results['initial_capital']:,.2f}")
        print(f"Final Capital:   ${results['final_capital']:,.2f}")
        print(f"Total Trades:    {results['total_trades']}")
        print("="*70 + "\n")


if __name__ == "__main__":
    print("Backtesting Module")
    print("Use this to test strategies on historical data")
