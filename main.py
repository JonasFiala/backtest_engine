from bot.broker import Broker
import pandas as pd
from typing import List, Optional, Union
from bot.datastruct import Timeframe, Index, Indicator
from dataclasses import dataclass
from tqdm import tqdm


"""
# data["ema8"] = data["Close"].ewm(span=8, adjust=False).mean()
# data["ema13"] = data["Close"].ewm(span=13, adjust=False).mean()
# data["ema21"] = data["Close"].ewm(span=21, adjust=False).mean()
# data["ema55"] = data["Close"].ewm(span=55, adjust=False).mean()
# def calculate_rsi(data: pd.DataFrame, period: int = 14) -> pd.Series:
#     delta = data['Close'].diff()
#     gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
#     loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
#     rs = gain / loss
#     rsi = 100 - (100 / (1 + rs))
#     return rsi

# for tf in list(data.values()):
#     print("saved")
#     tf.df.to_csv(f"data\\data_{tf.timeframe}.csv")


    
    
# === Step 2: Resample to 1-hour OHLCV ===


# df_1h = base_data.resample("1h").agg({
#     "Open": "first",
#     "High": "max",
#     "Low": "min",
#     "Close": "last",
#     "Volume": "sum"
# })

# === Step 3: Forward-fill 1H data to align with 1M index ===
# df_1h_ffill = df_1h.reindex(df_1m.index, method="ffill")


# === Step 4: Rename columns for clarity ===


# === Step 5: Join 1M and 1H data ===
"""

opened = 0
closed = 0
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
        # if self.position is not None:
        #     print(f"Checking position: {self.position}")
        #     print(f"strategy_tf{self.timeframe}")
        #     print(f"positions: {broker.positions}")
        #     broker.close_position(self.position)
        #     self.position = None
        #     global closed
        #     closed+=1
        #     print(f"closed:{closed}")
        # if data[0]["Close"] < data[0]["Open"]:
        #     self.position = broker.market_order("btc", "long", 0.1, stop_loss=100, take_profit=200)
        #     global opened
        #     opened += 1
        #     print(f"opened: {opened, len(broker.positions)}")
        if self.position is not None:
            broker.close_position(self.position)
        if data[0]["Close"] < data[0]["Open"]:
            broker.market_order("btc", "long", 0.1)

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

"""
def process_data(data_dict: dict[str, pd.DataFrame]) -> dict[str, dict[str, Timeframe]]:
    tf_lists = [tf for tfs in chosen_tf.values() for tf in tfs]

    data: dict[str, dict[str, Timeframe]] = {tf: {} for symbol in }
    print(data)
    indexes = gen_indexes(chosen_tf)

    for symbol, df in data_dict.items():
        df.drop("Unnamed: 0", axis=1, inplace=True)

    for symbol, tfs in chosen_tf.items():
        for tf in tfs:
                tf_data = data_dict[symbol].resample(tf, label="right", closed="right").agg({
                    "Open": "first",
                    "High": "max",
                    "Low": "min",
                    "Close": "last",
                    "Volume": "sum"
                }).sort_index()
                data[tf][symbol] = Timeframe(tf_data, tf, indexes[tf])
    
    print(data[])
    return data
"""

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

strategies: List[Strategy] = [strategy1(timeframe="30min"), strategy1(timeframe="1h"), strategy1(timeframe="4h")]

    

chosen_tf: dict[str, List[str]] = get_chosen_tf(strategies)
all_tf: List[str] = list(set([tf for tfs in chosen_tf.values() for tf in tfs]))

indexes: dict[str, Index] = {}
data: dict[str, dict[str, Timeframe]] = {tf:{} for tf in all_tf}
indexes = gen_indexes(all_tf)

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
        data[tf][i] = Timeframe(tf_data, tf, indexes[tf])



print(data)

    
    




base_data_first = list(base_data.values())[0]

pbar = tqdm(total=len(base_data_first), desc="Running Engine", unit="steps")

broker = Broker(data["1min"])

for i in range(1,len(base_data_first)):
    broker.check_orders()
    broker.check_positions()
    broker.update_equity()
    for tf in all_tf:
        if i%TF_CNV[tf] == 0:
            for strategy in [strategy for strategy in strategies if strategy.timeframe == tf]:
                if strategy.timeframe == tf:
                    strategy_symbols = list(strategy.requirements.keys())
                    strategy.step({symbol: data[tf][symbol] for symbol in strategy_symbols})
            indexes[tf].value += 1
    pbar.update(1)

all_df: List[pd.DataFrame] = []
for tf in chosen_tf:
    df = data[tf].df.rename(columns=lambda col: f"{col}_{tf}")
    all_df.append(df)


# for df in all_df:
#     df.index = df.index.tz_localize(None)  # Remove timezone info if present

conect_df = pd.concat(all_df, axis=1).sort_index()
print(conect_df)
conect_df.to_csv("connected_data.csv")


print([i.value for i in indexes.values()])
pbar.close()


