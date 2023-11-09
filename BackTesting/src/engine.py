import pandas as pd
from matplotlib import pyplot as plt

class Engine():
    def __init__(self, initial_cash = 1000) -> None:
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.logs = None
        self.current_position = 0
        self.total_buy_trades = 0
        self.total_sell_trades = 0
        self.metrics = {}
        self.assets = 0
        self.status = 0
        self.net_value  = self.initial_cash
        self.net_values_list = []
        self.net_asset_list = []


    def add_logs(self, logs: pd.DataFrame) -> None:
        self.logs = logs
    
    def run(self) -> None:
        ## iterate over eachrow of dataframe self.logs
        self.logs['status'] = 0
        self.logs['assets'] = 0
        self.logs['cash'] = 0
        self.logs['net_value'] = 0
        for row in self.logs.itertuples():
            signal = int(row.logs)
            price = row.open
            timestamp = row.Index
            close = row.close

            if (self.status + signal) not in [-1, 0, 1]:
                print(f"Invalid trade signal at {timestamp}")
            
            if self.net_value <=0:
                print(f"maa chud gayi at {timestamp}")
                exit(1)

            self.assets += signal * self.cash / price
            self.cash -= signal * self.cash
            self.net_value = self.cash + self.assets * price
            self.status += signal
            self.logs.iloc[timestamp]['status'] = self.status
            self.logs.iloc[timestamp]['assets'] = self.assets
            self.logs.iloc[timestamp]['cash'] = self.cash
            self.logs.iloc[timestamp]['net_value'] = self.net_value
            self.net_values_list.append(self.net_value)
            self.net_asset_list.append(self.assets)
            # print(f"Net value {self.net_value}")
        

        if self.assets > 0:
            self.cash = price * self.assets
            self.assets = 0
        if self.assets < 0:
            self.cash -= price * self.assets
            self.assets = 0

    def plot(self) -> None:
        plt.plot(self.net_asset_list)
        plt.show()

    def get_metrics(self) -> dict:
        self.metrics["max_drawdown"] = (max(self.net_values_list) - min(self.net_values_list))/max(self.net_values_list)*100
        return self.metrics
        