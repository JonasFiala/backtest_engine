from bot.broker import Broker
import pandas as pd
from typing import List, Optional, Union
from bot.datastruct import Timeframe, Index, Indicator
from dataclasses import dataclass
from tqdm import tqdm
from collections import defaultdict

class Strategy:
    def __init__(self, name: str, requirements: dict[str, List[str]], timeframe: str, indicators: Optional[List[str]] = None, params: Optional[dict] = None):
        self.name = name
        self.requirements = requirements
        self.timeframe = timeframe
        self.indicators = indicators if indicators is not None else []
        self.params = params if params is not None else {}
        self.position = None
class strategy1(Strategy):
    def __init__(self, timeframe: str):
        super().__init__(
            name="Strategy1",
            timeframe=timeframe,
            requirements={"btc": []},
        )

    def step(self, data: Union[Timeframe, List[Timeframe]]):
        data = data["btc"]
        if self.position is not None:
            broker.close_position(self.position)
            self.position = None
        if data[0]["Close"] < data[0]["Open"]:
            self.position = broker.market_order("btc", "long", 0.1)

def gen_indexes(tf_list: List[str]) -> dict[str, Index]:
    """initializes indexes of chosen tfs"""
    return {tf: Index() for tf in tf_list}

def check_tfs(all_tf: List[str]) -> None:
    """Checks if all chosen timeframes are supported"""
    for tf in all_tf:
        if tf not in SUPPORTED_TF:
            raise ValueError(f"Unsupported timeframe: {tf}. Supported timeframes are: {SUPPORTED_TF}")

def get_chosen_tf(strategies: Strategy) -> dict[str, List[str]]:
    temp_list: List[dict[str, str]] = []
    symbols_required: List[str] = []
    for strategy in strategies:
        symbol_requirement: str = list(strategy.requirements.keys())[0]
        temp_list.append({symbol_requirement: strategy.timeframe})
        symbols_required.append(symbol_requirement)
    symbols_required = list(set(symbols_required))
    ch_tf: dict[str, List[str]] = {}
    for i in symbols_required:
        ch_tf[i] = ["1min"]


    for symbol, tf in [item for d in temp_list for item in d.items()]:
        ch_tf[symbol].append(tf)
    
    for symbol in ch_tf.keys():#delete duplicates
        ch_tf[symbol] = list(set(ch_tf[symbol]))
    return ch_tf

def data_foo(base_data:dict[str, pd.DataFrame], chosen_tf: dict[str, List[str]], all_tf: List[str]) -> dict[str, dict[str, Timeframe]]:
    data_temp = {tf:{} for tf in all_tf}
    for df in base_data.values():
        unvanted = ["Unnamed: 0", "timestamp"]
        for i in unvanted:
            if i in df.columns.to_list():
                df.drop(i, axis=1)
        
    for i, tfs in chosen_tf.items():
        for tf in tfs:
            tf_data = base_data[i].resample(tf, label="right", closed="right").agg({
                "Open": "first",
                "High": "max",
                "Low": "min",
                "Close": "last",
                "Volume": "sum"
            }).sort_index()
            data_temp[tf][i] = Timeframe(tf_data, tf, indexes[tf])
    return data_temp

def sort_strategies(strategies: List[Strategy]) -> dict[Strategy]:
    srt_strategies = defaultdict(list)
    for strategy in strategies:
        srt_strategies[strategy.timeframe].append(strategy)
    return srt_strategies

def pnt_results():
    print(f"Final cash: {broker.equity[-1]}")
    print(f"Max drawdown {broker.max_drawdown}")
    print(f"Winrate {broker.winrate}")

SUPPORTED_TF = ["1min", "5min", "15min", "30min", "1h", "4h", "1d"]
TF_CNV = {
    "1min": 1,
    "5min": 5,
    "15min": 15,
    "30min": 30,
    "1h": 60,
    "4h": 240,
    "1d": 1440
}


btc_data = pd.read_csv("data_btc.csv", parse_dates=["Date"], index_col="Date")
eth_data = pd.read_csv("data_eth.csv", parse_dates=["Date"], index_col="Date")
base_data:dict[str, pd.DataFrame] = {}
base_data["btc"] = btc_data
base_data["eth"] = eth_data

strategies: List[Strategy] = [strategy1(timeframe="1min")]

chosen_tf: dict[str, List[str]] = get_chosen_tf(strategies)
all_tf: List[str] = list(set([tf for tfs in chosen_tf.values() for tf in tfs]))

indexes: dict[str, Index] = {}
data: dict[str, dict[str, Timeframe]] = {}
indexes = gen_indexes(all_tf)    


data = data_foo(base_data, chosen_tf, all_tf)


base_data_first = list(base_data.values())[0]
broker = Broker(data["1min"])
srt_strategies = sort_strategies(strategies)

pbar = tqdm(total=len(base_data_first), desc="Running Engine", unit="steps")
for i in range(1,int(len(base_data_first))):
    broker.check_orders()
    broker.check_positions()
    broker.update_equity()
    for tf in all_tf:
        if i%TF_CNV[tf] == 0:
            for strategy in srt_strategies[tf]:
                if strategy.timeframe == tf:
                    strategy_symbols = list(strategy.requirements.keys())
                    strategy.step({symbol: data[tf][symbol] for symbol in strategy_symbols})
            indexes[tf].value += 1
    pbar.update(1)
pbar.close()

pnt_results()


all_df: List[pd.DataFrame] = []
for symbol, tfs in chosen_tf.items():
    for tf in tfs:
        df = data[tf][symbol].df.rename(columns=lambda col: f"{symbol}_{col}_{tf}")
        all_df.append(df)



conect_df = pd.concat(all_df, axis=1).sort_index()
print(conect_df)
conect_df.to_csv("connected_data.csv")


print([i.value for i in indexes.values()])


