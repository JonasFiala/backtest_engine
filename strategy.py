from typing import Optional
from .broker import Broker
from .datastruct import Position, Data
import pandas as pd

class Strategy:
    "Base class for every strategy"
    def __init__(self, requirements: list[str], broker: Broker = None, data: dict[str, Data] = None):
        self.requirements = requirements
        self.broker = broker
        self.positions = []
        self.data: dict[str, Data] = data


    def market_long(self, symbol: str, size: float, stop_loss: Optional[float] = None, take_profit: Optional[float] = None) -> Position:
        return self.broker.market_order(
            symbol=symbol,
            side="long",
            size=size,
            stop_loss=stop_loss,
            take_profit=take_profit
        )

    def market_short(self, symbol: str, size: float, stop_loss: Optional[float] = None, take_profit: Optional[float] = None) -> Position:
        return self.broker.market_order(
            symbol=symbol,
            side="short",
            size=size,
            stop_loss=stop_loss,
            take_profit=take_profit
        )

    def limit_long(self, symbol: str, price: float, size: float, time_limit: Optional[pd.Timestamp] = None, stop_loss: Optional[float] = None, take_profit: Optional[float] = None) -> None:
        self.broker.limit_order(
            symbol=symbol,
            side="long",
            price=price,
            size=size,
            stop_loss=stop_loss,
            take_profit=take_profit,
            time_limit=time_limit
        )

    def limit_short(self, symbol: str, price: float, size: float, time_limit: Optional[pd.Timestamp] = None, stop_loss: Optional[float] = None, take_profit: Optional[float] = None) -> None:
        self.broker.limit_order(
            symbol=symbol,
            side="long",
            price=price,
            size=size,
            stop_loss=stop_loss,
            take_profit=take_profit,
            time_limit=time_limit
        )