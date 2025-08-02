from dataclasses import dataclass
from typing import Optional, Literal, Union, List
import pandas as pd

import pandas as pd


"""

@dataclass
class Index:
    value: int = 0

class Indicator:
    def __init__(self, df: pd.DataFrame, timeframe: str, index: Optional[Index] = None):
        self.df: pd.DataFrame = df
        self.timeframe: str = timeframe
        self.index: Index = index if index is not None else Index()

    def __getitem__(self, item: Union[str, int]) -> pd.Series:
        if isinstance(item, str):
            return self.df[item]
        elif isinstance(item, int):
            return self.df.iloc[item]
        else:
            raise TypeError("Key must be a string or an integer index.")




class Timeframe():
    def __init__(self, df: pd.DataFrame, timeframe: str, index: Optional[Index]):
        self.df: pd.DataFrame = df
        self.timeframe: str = timeframe
        self.index: Index = index if index is not None else Index()
        self.indicators: List[Indicator] = []

    def __getitem__(self, item: Union[str, int]) -> pd.Series:
        if isinstance(item, str):
            return self.df[item]
        elif isinstance(item, int):
            target_index = self.index.value + item
            try:
                return self.df.iloc[target_index]
            except IndexError:
                return None
        else:
            raise TypeError("Key must be a string or an integer index.")
"""

@dataclass
class Index:
    value: int = 0

class Indicator:
    def __init__(self, df: pd.DataFrame, timeframe: str, index: Optional[Index] = None):
        self.df: pd.DataFrame = df
        self.timeframe: str = timeframe
        self.index: Index = index if index is not None else Index()

    def __getitem__(self, item: Union[str, int]) -> pd.Series:
        if isinstance(item, str):
            return self.df[item]
        elif isinstance(item, int):
            return self.df.iloc[item]
        else:
            raise TypeError("Key must be a string or an integer index.")




class Timeframe():
    def __init__(self, df: pd.DataFrame, timeframe: str, index: Optional[Index]):
        self.df: pd.DataFrame = df
        self.timeframe: str = timeframe
        self.index: Index = index if index is not None else Index()
        self.indicators: List[Indicator] = []

    def __getitem__(self, item: Union[str, int]) -> pd.Series:
        if isinstance(item, str):
            return self.df[item]
        elif isinstance(item, int):
            target_index = self.index.value + item
            try:
                return self.df.iloc[target_index]
            except IndexError:
                return None
        else:
            raise TypeError("Key must be a string or an integer index.")

@dataclass()
class Index():
    """Shared index for data access"""
    value: int = 0

class Data:
    """Handles data, enables accesing current pd.series by [0] last [-1] and next [1].
    data = Data("path.csv")
    current pd.series: data[0]
    current close price: data[0]['Close']

    in strategy class data is wrapped in a dict with symbol as key so you access it like this:
    self.data[symbol][0] for current pd.series
    self.data[symbol][0]['Volume'] for current close price
    self.data[symbol].data to access the whole dataframe
    """
    def __init__(self, source: str, index: Index, multiplier: float = 1):
        df = pd.read_csv(source, parse_dates=["Date"], index_col="Date")
        self.data = df
        self.index = index
        self.indicators = {}
        self.multiplier = multiplier

    def __getitem__(self, input_index: int):
        my_index = int(self.index.value * self.multiplier)
        target_index = my_index + input_index
        try:
            return self.data.iloc[target_index]
        except IndexError:
            return None
        
    def calculate_ema(self, period: int, column: str = "Close") -> pd.Series:
        ema_key = f"ema{period}"
        if ema_key not in list(self.data.columns):
            self.data[ema_key] = self.data[column].ewm(span=period, adjust=False).mean()
    
    def calculate_rsi(self, period: int = 14) -> pd.Series:
        if 'rsi' not in list(self.data.columns):
            delta = self.data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            self.indicators['rsi'] = rsi
            self.data['rsi'] = rsi

    # def ind_val(self, indicator_key: str, offset: int = 0) -> float:
    #     """Get the current or relative value of an indicator."""
    #     if indicator_key in self.indicators:
    #         target_index = self.index.value + offset
    #         try:
    #             return self.indicators[indicator_key].iloc[target_index]
    #         except IndexError:
    #             return None
    #     raise KeyError(f"Indicator '{indicator_key}' not found.")


class Position:
    def __init__(
        self,
        symbol: str,
        side: Literal["long", "short"],
        entry_price: float,
        size: float,
        entry_time: pd.Timestamp,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
    ):
        self.symbol = symbol
        self.side = side
        self.entry_price = entry_price
        self.size = size
        self.entry_time = entry_time
        self.stop_loss = stop_loss
        self.take_profit = take_profit

    def __repr__(self):
        return (
            f"Position(symbol={self.symbol!r}, side={self.side!r}, "
            f"entry_price={self.entry_price!r}, size={self.size!r}, "
            f"entry_time={self.entry_time!r}, stop_loss={self.stop_loss!r}, "
            f"take_profit={self.take_profit!r})"
        )

    @property
    def units(self) -> float:
        return self.size / self.entry_price

    def calculate_pnl(self, current_price: float) -> float:
        multiplier = 1 if self.side == "long" else -1
        return (current_price - self.entry_price) * self.units * multiplier
    
    def __eq__(self, other):
        return isinstance(other, Position) and self is other  

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