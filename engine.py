from typing import List, Dict
from .strategy import Strategy
from .broker import Broker
from .datastruct import Data

index:int = 0
class Engine:
    def __init__(self, strategies: List[Strategy], data_sources: Dict[str, str]):
        global DATA
        DATA = {symbol: Data(source) for symbol, source in data_sources.items()}
        self.data = list(DATA.values())[0]	
        self.broker = Broker()
        for strategy in strategies:
            strategy.broker = self.broker
            strategy.data = DATA

        self.strategies: List[Strategy] = strategies

    def run(self):
        """Strarts the simulation"""
        global index
        while (True):
            index += 1

            for strategy in self.strategies:
                strategy.step()
            self.broker.check_orders()
            self.broker.check_positions()
            self.broker.update_equity()

            if (self.data[1] is None):
                break
        self.broker.trades
        print("Final cash:", self.broker.cash)