from typing import List, Optional
from .datastruct import Position, Trade, Limit_order, Data
import pandas as pd

class Broker:
    def __init__(self, cash: float = 10_000):
        global DATA
        self.positions: List[Position] = []
        self.initial_cash = cash
        self.cash = cash
        self.orders: List[Limit_order] = [] 
        self.trades: List[Trade] = []
        self.equity = []
        self.data: dict[str, Data] = DATA

    def current_price(self, symbol: str) -> pd.Series:
        return self.data[symbol][0]
    
    @property
    def current_time(self) -> pd.Timestamp:
        first_key = list(self.data.keys())[0]
        return self.data[first_key][0].name

    def market_order(self, symbol: str, side: str, size: float, 
                     stop_loss: Optional[float] = None,
                     take_profit: Optional[float] = None) -> bool:
        """Executes a market order"""
        cash_amount = self.cash * size 
        if cash_amount > self.cash:
            raise ValueError(f"Insufficient cash to open position: {cash_amount} > {self.cash}")
        
        fliper = 1 if side == "long" else -1
        try:
            check_sl = stop_loss*fliper > self.current_price(symbol)["Close"]*fliper
            check_tp = take_profit*fliper < self.current_price(symbol)["Close"]*fliper
            if check_sl or check_tp:
                raise ValueError("\n\n!!Stop loss or take profit is not valid for current price!!\n\n")
        except:
            pass


        position = Position(
            symbol=symbol,
            side=side,
            entry_price=self.current_price(symbol)["Close"],
            size=cash_amount, 
            entry_time=self.current_time,
            stop_loss=stop_loss,
            take_profit=take_profit
        )
        self.positions.append(position)
        self.cash -= cash_amount
        print(f"Market position opened: {position}\n")
        return position


    def limit_order(self, symbol: str, side: str, price: float,
                        size: float, 
                        time_limit: Optional[pd.Timestamp] = None,
                        stop_loss: Optional[float] = None,
                        take_profit: Optional[float] = None) -> bool:
        """Creates a limit order"""
        cash_amount = self.cash * size
        order = Limit_order(
            symbol=symbol,
            side=side,
            price=price,
            size=cash_amount, 
            time_limit=time_limit,
            stop_loss=stop_loss,
            take_profit=take_profit
        )
        self.orders.append(order)
        print(f"Limit order placed: {order}\n")
        return True

    def close_position(self, position: Position) -> None:
        """Closes a position at current price"""
        price = self.current_price(position.symbol)["Close"] 
        pnl = position.calculate_pnl(price)
        current_value = position.units * price
        self.cash += current_value
        trade = Trade(
            symbol=position.symbol,
            side=position.side,
            entry_price=position.entry_price,
            exit_price=price,
            size=position.size,
            entry_time=position.entry_time,
            exit_time=self.current_time,
            pnl=pnl,
            stop_loss=position.stop_loss,
            take_profit=position.take_profit
        )
        self.trades.append(trade)
        self.positions.remove(position)
        print(f"Position closed: {trade}\n")

    def update_equity(self) -> None:
        "Logs the current equity value"
        positions_value = sum(
            pos.calculate_pnl(self.current_price(pos.symbol)) 
            for pos in self.positions
        )
        self.equity.append(self.cash + positions_value)

    def check_orders(self):
        "Check every order if it can be executed"
        for order in self.orders[:]: 
            if order.time_limit is not None and order.time_limit < self.current_time:
                self.orders.remove(order)
                continue
            
            current_price = self.current_price(order.symbol)["Close"]
            if (order.side == "long" and current_price <= order.price) or \
               (order.side == "short" and current_price >= order.price):
                if self.can_trade(order.size, current_price):
                    self.market_order(
                        symbol=order.symbol, 
                        side=order.side, 
                        size=order.size,
                        price=current_price,  # Pass current price
                        stop_loss=order.stop_loss,
                        take_profit=order.take_profit
                    )
                    self.orders.remove(order)

    def check_positions(self):
        "Check every open position if sl or tp has been hit"
        for position in self.positions[:]: 
            if position.stop_loss:
                if (position.side == "long" and self.current_price(position.symbol)["Low"] <= position.stop_loss) or \
                   (position.side == "short" and self.current_price(position.symbol)["High"] >= position.stop_loss):
                    self.close_position(position, position.stop_loss)
                    continue
                    
            if position.take_profit:
                if (position.side == "long" and self.current_price(position.symbol)["High"] >= position.take_profit) or \
                   (position.side == "short" and self.current_price(position.symbol)["Low"] <= position.take_profit):
                    self.close_position(position, position.take_profit)