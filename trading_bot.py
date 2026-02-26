"""
Simplified Trading Bot - Core Strategy
Premarket Breakout with Retest Confirmation
"""

import pandas as pd
import numpy as np
from datetime import datetime, time, date
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import logging
import config

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)


class Direction(Enum):
    """Trade direction"""
    LONG = "LONG"
    SHORT = "SHORT"


@dataclass
class Trade:
    """Represents a single trade"""
    ticker: str
    direction: Direction
    entry_price: float
    stop_loss: float
    take_profit: float
    entry_time: datetime
    exit_price: Optional[float] = None
    exit_time: Optional[datetime] = None
    pnl: Optional[float] = None
    status: str = "OPEN"


@dataclass
class PremarketLevels:
    """Store premarket high and low"""
    high: float
    low: float
    date: date


class TradingBot:
    """Main trading bot"""

    def __init__(self, tickers: List[str], risk_reward: float = 2.0):
        self.tickers = tickers
        self.risk_reward = risk_reward

        # Store premarket levels for each ticker
        self.premarket_levels: Dict[str, PremarketLevels] = {}

        # Track completed trades
        self.completed_trades: List[Trade] = []

        # Volume history for analysis
        self.volume_history: Dict[str, List[float]] = {t: [] for t in tickers}

        # Open trades by ticker
        self.open_trades: Dict[str, Optional[Trade]] = {t: None for t in tickers}

        logger.info(f"Trading bot initialized for {tickers}")
        logger.info(f"Risk-Reward ratio: {risk_reward}:1")

    def update_premarket_levels(self, ticker: str, data: pd.DataFrame):
        """
        Calculate premarket high and low

        Args:
            ticker: Trading symbol
            data: DataFrame with columns ['timestamp', 'high', 'low', 'volume']
        """
        # Filter for premarket hours (4:00 AM - 9:30 AM)
        premarket_data = data[
            (data['timestamp'].dt.time >= time(4, 0)) &
            (data['timestamp'].dt.time < time(9, 30))
        ]

        if len(premarket_data) == 0:
            logger.warning(f"No premarket data for {ticker}")
            return

        pm_high = premarket_data['high'].max()
        pm_low = premarket_data['low'].min()

        self.premarket_levels[ticker] = PremarketLevels(
            high=pm_high,
            low=pm_low,
            date=datetime.now().date()
        )

        logger.info(f"{ticker} Premarket - High: {pm_high:.2f}, Low: {pm_low:.2f}")

    def calculate_average_volume(self, ticker: str) -> float:
        """Calculate average volume for a ticker"""
        volumes = self.volume_history[ticker]
        if len(volumes) < 20:
            return np.mean(volumes) if volumes else 0
        return float(np.mean(volumes[-20:]))  # Last 20 bars

    def is_strong_volume(self, current_volume: float, avg_volume: float) -> bool:
        """Check if volume is strong (>150% of average)"""
        return current_volume >= (avg_volume * 1.5)

    def is_lesser_volume(self, current_volume: float, breakout_volume: float) -> bool:
        """Check if volume is lesser (<70% of breakout)"""
        return current_volume <= (breakout_volume * 0.7)

    def process_bar(self, ticker: str, bar: Dict) -> Optional[Trade]:
        """
        Process a single price bar

        Args:
            bar: Dict with keys ['timestamp', 'open', 'high', 'low', 'close', 'volume']

        Returns:
            Trade object if trade executed, None otherwise
        """
        # Update volume history
        self.volume_history[ticker].append(bar['volume'])

        logger.debug(f"{ticker} - Price: {bar['close']:.2f}, Volume: {bar['volume']}")

        # Ensure we have premarket levels
        levels = self.premarket_levels.get(ticker)
        if not levels:
            return None

        ts = bar.get('timestamp')
        if hasattr(ts, 'time'):
            current_time = ts.time()
        else:
            current_time = None

        # ENTRY: Only after market open (9:30)
        market_open = __import__('datetime').time(9, 30)

        # Check for existing open trade and handle exits
        open_trade = self.open_trades.get(ticker)
        if open_trade:
            # Check for TP or SL hits
            tp = open_trade.take_profit
            sl = open_trade.stop_loss
            exit_price = None
            # If both touched in same bar, conservatively assume SL
            if bar['low'] <= sl:
                exit_price = sl
            elif bar['high'] >= tp:
                exit_price = tp

            if exit_price is not None:
                open_trade.exit_price = exit_price
                open_trade.exit_time = bar['timestamp']
                if open_trade.direction == Direction.LONG:
                    open_trade.pnl = (open_trade.exit_price - open_trade.entry_price) * config.POSITION_SIZE
                else:
                    open_trade.pnl = (open_trade.entry_price - open_trade.exit_price) * config.POSITION_SIZE
                open_trade.status = 'CLOSED'
                self.completed_trades.append(open_trade)
                self.open_trades[ticker] = None
                logger.info(f"Closed {open_trade.direction.value} {ticker} entry={open_trade.entry_price:.2f} exit={open_trade.exit_price:.2f} pnl={open_trade.pnl:+.2f}")
                return open_trade

        # Try to open a new trade if none open and it's market hours
        if not open_trade and current_time and current_time >= market_open:
            avg_vol = self.calculate_average_volume(ticker)
            if self.is_strong_volume(bar['volume'], avg_vol):
                # Long breakout
                if bar['close'] > levels.high:
                    entry = bar['close']
                    sl = levels.high - (levels.high * config.STOP_LOSS_BUFFER)
                    tp = entry + (entry - sl) * self.risk_reward
                    trade = Trade(
                        ticker=ticker,
                        direction=Direction.LONG,
                        entry_price=entry,
                        stop_loss=sl,
                        take_profit=tp,
                        entry_time=bar['timestamp']
                    )
                    self.open_trades[ticker] = trade
                    logger.info(f"Opened LONG {ticker} entry={entry:.2f} sl={sl:.2f} tp={tp:.2f}")
                    return None

                # Short breakout
                if bar['close'] < levels.low:
                    entry = bar['close']
                    sl = levels.low + (levels.low * config.STOP_LOSS_BUFFER)
                    tp = entry - (sl - entry) * self.risk_reward
                    trade = Trade(
                        ticker=ticker,
                        direction=Direction.SHORT,
                        entry_price=entry,
                        stop_loss=sl,
                        take_profit=tp,
                        entry_time=bar['timestamp']
                    )
                    self.open_trades[ticker] = trade
                    logger.info(f"Opened SHORT {ticker} entry={entry:.2f} sl={sl:.2f} tp={tp:.2f}")
                    return None

        return None

    def get_performance_summary(self) -> Dict:
        """Calculate performance statistics"""
        if not self.completed_trades:
            return {"message": "No trades yet"}

        total_trades = len(self.completed_trades)
        winning_trades = [t for t in self.completed_trades if t.pnl and t.pnl > 0]

        win_rate = len(winning_trades) / total_trades * 100 if total_trades else 0
        total_pnl = sum(t.pnl for t in self.completed_trades if t.pnl)

        return {
            "total_trades": total_trades,
            "winning_trades": len(winning_trades),
            "win_rate": f"{win_rate:.2f}%",
            "total_pnl": f"${total_pnl:+,.2f}"
        }


if __name__ == "__main__":
    # Quick test
    print("Trading Bot Core Module")
    print("This file contains the main trading logic")

    # Create a bot instance
    bot = TradingBot(tickers=['MNQ'], risk_reward=2.0)
    print(" Bot created successfully")
    print(f" Monitoring: {bot.tickers}")
