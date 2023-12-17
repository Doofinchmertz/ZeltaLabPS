import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import os
from empyrical import max_drawdown

class Engine():
    def __init__(self, initial_cash = 1000) -> None:
        self.logs = None
        self.initial_cash = initial_cash
        self.cash = self.initial_cash
        self.status = 0
        self.net_pnl = 0
        self.max_total_loss_capacity = - 100*self.initial_cash
        self.daily_pnl_lst = []
        self.net_pnl_lst = []
        self.metrics = {}
        self.gross_profit = 0
        self.gross_loss = 0
        self.total_trades_closed = 0
        self.largest_winning_trade = 0
        self.largest_losing_trade = 0
        self.min_net_pnl = 1e10
        self.winning_trades_lst = []
        self.losing_trades_lst = []
        self.num_win_trades = 0
        self.num_lose_trades = 0
        self.metrics_logs = pd.DataFrame(columns=['Trade PnL', 'Net PnL'])
        self.last_bough_amt = 0
        self.last_sold_amt = 0
        self.transaction_cost = 0.0015
        self.total_transaction_cost = 0
        self.returns_lst = []


    def add_logs(self, logs: pd.DataFrame) -> None:
        self.logs = logs

    def run(self) -> None:

        for row in self.logs.itertuples():
            signal = int(row.signal)
            open = row.open
            timestamp = row.datetime
            close = row.close
            price = close

            if (signal) not in [-1, 0, 1]:
                print(f"Invalid trade signal at {timestamp}")
                continue

            if(self.status + signal) not in [-1, 0, 1]:
                print(f"Invalid trade signal at {timestamp}")
                continue

            if(self.net_pnl < self.max_total_loss_capacity):
                print(f"maa chud gayi at {timestamp}")
                exit(1)

            trade_pnl = 0

            if signal == 1:
                if(self.status == 0):
                    self.assets = self.cash / price
                    self.last_bough_amt = self.cash
                    self.cash = 0
                elif(self.status == -1):
                    trade_pnl = self.last_sold_amt + self.assets * price
                    trade_pnl -= self.transaction_cost*self.last_sold_amt
                    self.returns_lst.append(trade_pnl/self.last_sold_amt)
                    self.total_transaction_cost += self.transaction_cost*self.last_sold_amt
                    self.net_pnl += trade_pnl
                    self.assets = 0
                    self.total_trades_closed += 1
                    self.cash -= self.last_sold_amt
                else:
                    print(f"Invalid trade signal at {timestamp}")
                    continue

            if signal == -1:
                if(self.status == 0):
                    self.assets = -self.cash / price
                    self.last_sold_amt = self.cash
                    self.cash += self.cash
                elif(self.status == 1):
                    trade_pnl = self.assets * price - self.last_bough_amt
                    trade_pnl -= self.transaction_cost * self.last_bough_amt
                    self.returns_lst.append(trade_pnl/self.last_bough_amt)
                    self.total_transaction_cost += self.transaction_cost * self.last_bough_amt
                    self.net_pnl += trade_pnl
                    self.assets = 0
                    self.total_trades_closed += 1
                    self.cash = self.last_bough_amt
                else:
                    print(f"Invalid trade signal at {timestamp}")
                    continue

            ## Updating status
            self.status += signal
            self.daily_pnl_lst.append(trade_pnl)
            self.net_pnl_lst.append(self.net_pnl)
            self.cash += trade_pnl
            if trade_pnl > 0:
                self.gross_profit += trade_pnl
                self.largest_winning_trade = max(self.largest_winning_trade, trade_pnl)
                self.winning_trades_lst.append(trade_pnl)
                self.num_win_trades += 1
            elif trade_pnl < 0:
                self.gross_loss += trade_pnl
                self.largest_losing_trade = min(self.largest_losing_trade, trade_pnl)
                self.losing_trades_lst.append(trade_pnl)
                self.num_lose_trades += 1

            self.min_net_pnl = min(self.min_net_pnl, self.net_pnl)

            # if(signal != 0):
            #     print(f"Trade at {timestamp} with price {price} and signal {signal}, total assets : {self.assets}, trade_pnl : {trade_pnl}, net_pnl : {self.net_pnl}, net_cash : {self.cash}")

        if self.assets > 0:
            trade_pnl = self.assets * close - self.last_bough_amt
            self.net_pnl += trade_pnl
            self.assets = 0
            self.daily_pnl_lst.append(trade_pnl)
            self.net_pnl_lst.append(self.net_pnl)
            self.total_trades_closed += 1
            self.min_net_pnl = min(self.min_net_pnl, self.net_pnl)
            if trade_pnl > 0:
                self.gross_profit += trade_pnl
                self.largest_winning_trade = max(self.largest_winning_trade, trade_pnl)
                self.winning_trades_lst.append(trade_pnl)
                self.num_win_trades += 1
            elif trade_pnl < 0:
                self.gross_loss += trade_pnl
                self.largest_losing_trade = min(self.largest_losing_trade, trade_pnl)
                self.losing_trades_lst.append(trade_pnl)
                self.num_lose_trades += 1
            self.cash += trade_pnl
            
        elif self.assets < 0:
            trade_pnl = self.last_sold_amt + self.assets * close
            self.net_pnl += trade_pnl
            self.assets = 0
            self.daily_pnl_lst.append(trade_pnl)
            self.net_pnl_lst.append(self.net_pnl)
            self.total_trades_closed += 1
            self.min_net_pnl = min(self.min_net_pnl, self.net_pnl)
            if trade_pnl > 0:
                self.gross_profit += trade_pnl
                self.largest_winning_trade = max(self.largest_winning_trade, trade_pnl)
                self.winning_trades_lst.append(trade_pnl)
                self.num_win_trades += 1
            elif trade_pnl < 0:
                self.gross_loss += trade_pnl
                self.largest_losing_trade = min(self.largest_losing_trade, trade_pnl)
                self.losing_trades_lst.append(trade_pnl)
                self.num_lose_trades += 1
            self.cash += trade_pnl

    def plot(self)-> None:
        plt.plot(self.net_pnl_lst)
        plt.axhline(y=0, color='black', linestyle='--') # add this line to draw x-axis at y=0
        plt.title("Net PnL")
        plt.xlabel("Time")
        plt.ylabel("Net PnL")
        plt.show()

    def get_metrics(self) -> dict:
        self.metrics["Net PnL"] = self.net_pnl
        # self.metrics["Gross Profit"] = self.gross_profit
        # self.metrics["Gross Loss"] = self.gross_loss
        # self.metrics["Total Trades Closed"] = self.total_trades_closed
        # self.metrics["Sharpe Ratio"] = np.mean(np.array(self.daily_pnl_lst))/np.std(np.array(self.daily_pnl_lst))
        # self.metrics["Largest Winning Trade"] = self.largest_winning_trade
        # self.metrics["Largest Losing Trade"] = self.largest_losing_trade
        # self.metrics["Min Net PnL"] = self.min_net_pnl
        # self.metrics["Average Winning Trade"] = np.mean(np.array(self.winning_trades_lst))
        # self.metrics["Average Losing Trade"] = np.mean(np.array(self.losing_trades_lst))
        # self.metrics["Number of Winning Trades"] = self.num_win_trades
        # self.metrics["Number of Losing Trades"] = self.num_lose_trades
        # self.metrics["Final Cash"] = self.cash
        # self.metrics["Total Transaction cost"] = self.total_transaction_cost
        # self.metrics["Maximum Drawdown"] = max_drawdown(np.array(self.net_pnl_lst))
        return self.metrics