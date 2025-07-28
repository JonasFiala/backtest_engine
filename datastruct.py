from dataclasses import dataclass
from typing import Optional, Literal
import pandas as pd

import pandas as pd

class Data:
    """Handles data, enables accesing current pd.series by [0] last [-1] and next [1].
    data = Data("path.csv")
    current pd.series: data[0]
    current close price: data[0]['Close']

    in strategy class data is wrapped in a dict with symbol as key so you access it like this:
    self.data[symbol][0] for current pd.series
    self.data[symbol][0]['Volume'] for current close price"""
    def __init__(self, source: str):
        df = pd.read_csv(source, parse_dates=["Date"], index_col="Date")
        self.data = df

    def __getitem__(self, input_index: int):
        global index
        target_index = index + input_index
        try:
            return self.data.iloc[target_index]
        except IndexError:
            return None

@dataclass(frozen=True)
class Position:
    symbol: str
    side: Literal["long", "short"]
    entry_price: float
    size: float
    entry_time: pd.Timestamp
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

    @property
    def units(self) -> float:
        return self.size / self.entry_price

    def calculate_pnl(self, current_price: float) -> float:
        multiplier = 1 if self.side == "long" else -1
        return (current_price - self.entry_price) * self.units * multiplier

@dataclass(frozen=True)
class Limit_order:
    symbol: str
    side: Literal["long", "short"]
    price: float
    size: float
    time_limit: Optional[pd.Timestamp] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

@dataclass(frozen=True)
class Trade:
    symbol: str
    side: Literal["long", "short"]
    entry_price: float
    exit_price: float
    size: float
    entry_time: pd.Timestamp
    exit_time: pd.Timestamp
    pnl: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None