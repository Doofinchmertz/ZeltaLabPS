import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import os

class Engine():
    """
    This class is responsible for running the backtest and calculating the metrics
    """
    def __init__(self, initial_cash = 1000, gen_vis_logs = False) -> None:
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
        self.net_returns_list = []
        self.total_transaction_cost = 0
        self.transaction_fee = 0.001
        self.total_trades_closed = 0
        self.gross_loss = 0
        self.metrics_logs = pd.DataFrame(columns=['Net Returns', 'Net Value', 'Net Assets', 'Net Cash'])
        self.gen_vis_logs = gen_vis_logs


    def add_logs(self, logs: pd.DataFrame) -> None:
        self.logs = logs
    
    def run(self) -> None:
        ## iterate over eachrow of dataframe self.logs
        self.first_open = self.logs.iloc[0]['Open']
        
        for row in self.logs.itertuples():
            signal = int(row.signal)
            price = row.Open
            timestamp = row.datetime
            close = row.Close

            if signal not in [-1, 0, 1]:
                print(f"Invalid trade signal at {timestamp}")
                continue

            if (self.status + signal) not in [-1, 0, 1]:
                print(f"Invalid trade signal at {timestamp}")
                continue
            
            if self.net_value <=0:
                print(f"maa chud gayi at {timestamp}")
                exit(1)
            
            # self.assets += signal * self.cash / price
            # self.total_transaction_cost += self.transaction_fee * abs(signal * self.cash)
            # self.cash -= signal * self.cash
            trade_executed = False
            if signal == 1:
                if(self.cash > 0):
                    if(self.assets < 0 and self.assets + self.cash/(price * (1 + self.transaction_fee)) >= 0):
                        self.total_trades_closed += 1
                    self.assets += self.cash / (price * (1 + self.transaction_fee))
                    self.total_transaction_cost += self.transaction_fee * abs(self.cash/(1 + self.transaction_fee))
                    self.cash = 0
                    trade_executed = True
            if signal == -1:
                if(self.assets > 0):
                    self.cash += self.assets * price - self.transaction_fee * abs(self.assets * price)
                    self.total_transaction_cost += self.transaction_fee * abs(self.assets * price)
                    self.assets = 0
                    self.total_trades_closed += 1
                    trade_executed = True
                elif(self.assets == 0):
                    self.assets -= self.cash / price
                    self.total_transaction_cost += self.transaction_fee * abs(self.cash)
                    self.cash += self.cash - self.transaction_fee * abs(self.cash)
                    trade_executed = True

            if(self.cash + self.assets * price < self.net_value and trade_executed):
                self.gross_loss += (self.cash + self.assets * price) - self.net_value
            self.net_value = self.cash + self.assets * price
            self.status += signal
            self.net_values_list.append(self.net_value)
            self.net_asset_list.append(self.assets)
            self.net_returns_list.append((self.net_value - self.initial_cash)/self.initial_cash*100)
            if self.gen_vis_logs:
                self.metrics_logs = pd.concat([self.metrics_logs, pd.DataFrame([[self.net_returns_list[-1], self.net_value, self.assets, self.cash]], columns=['Net Returns', 'Net Value', 'Net Assets', 'Net Cash'])])
            if(signal != 0):
                print(f"Trade at {timestamp} with price {price} and signal {signal} and total assets {self.assets} and total cash {self.cash} and net value {self.net_value}")
            # print(f"Net value {self.net_value}")
        
        self.last_open = price

        if self.assets > 0:
            self.cash = price * self.assets
            self.assets = 0
            self.total_trades_closed += 1
        if self.assets < 0:
            self.cash -= price * self.assets
            self.assets = 0
            self.total_trades_closed += 1
        
        assert(self.assets == 0) ## Check if liquidated all assets in the end


    def plot(self) -> None:
        plt.plot(self.net_values_list)
        plt.show()

    def get_metrics(self) -> dict:
        if self.gen_vis_logs:
            if not os.path.exists("metric_logs"):
                os.makedirs("metric_logs")
            self.metrics_logs.to_csv("metric_logs/compounding_metric_logs.csv")
        self.metrics["Gross Profit"] = self.cash - self.initial_cash + self.total_transaction_cost
        self.metrics["Net Profit"] = self.cash - self.initial_cash 
        self.metrics["Total Trades Closed"] = self.total_trades_closed
        self.metrics["Strategy_PnL"] = self.metrics["Net Profit"]/self.initial_cash*100
        self.metrics["Buy and Hold PnL"] = (self.last_open - self.first_open - self.transaction_fee*(self.last_open + self.first_open))/self.first_open*100
        self.metrics["Gross Loss"] = self.gross_loss
        max_indx = np.argmax(np.array(self.net_values_list))
        self.metrics["Max Drawdown"] = (self.net_values_list[max_indx] - min(self.net_values_list[max_indx+1:]))/self.net_values_list[max_indx]*100
        self.metrics["Sharpe Ratio"] = np.mean(np.array(self.net_returns_list))/np.std(np.array(self.net_returns_list))
        return self.metrics
        