import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import os
import talib
from empyrical import max_drawdown

class Static_Engine():
    def __init__(self, log_name = None, static_trade_amount = 1000, without_transaction_cost = False, tick_sz = 5) -> None:
        self.logs = None
        self.each_trade_amount = static_trade_amount
        self.status = 0
        self.net_pnl = 0
        self.max_total_loss_capacity = - 100*self.each_trade_amount
        self.trade_pnl_lst = []
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
        self.assets = 0
        self.transaction_cost = 0.0015
        self.total_transaction_cost = 0
        if without_transaction_cost:
            self.transaction_cost = 0
        self.last_trade_open_time = None
        self.trade_holding_times = []
        self.immediate_losses = 0
        self.immediate_profits = 0
        self.min_time_diff = pd.Timedelta(minutes=tick_sz)
        self.log_name = log_name
        self.close_price_lst = []
        self.open_price_lst = []
        self.trade_returns = []
        self.annual_trade_returns = dict()

    def add_logs(self, logs: pd.DataFrame) -> None:
        self.logs = logs

    def run(self) -> None:
        self.close_price_lst = self.logs['close'].tolist()
        self.open_price_lst = self.logs['open'].tolist()
        self.logs['trade_pnl'] = 0
        self.logs['trade_pnl'] = self.logs['trade_pnl'].astype('float64')
        df = self.logs[self.logs['signal'] != 0]
        first_timestamp = None
        for row in df.itertuples():
            signal = int(row.signal)
            timestamp = row.datetime
            timestamp = pd.to_datetime(timestamp)
            if first_timestamp is None:
                first_timestamp = timestamp
                self.annual_trade_returns[str(timestamp.year)] = list()
            year_difference = timestamp.year - first_timestamp.year
            if year_difference>=1:
                self.annual_trade_returns[str(timestamp.year)] = list()
                first_timestamp = timestamp

            close = row.close
            open = row.open
            price = close
            trade_closed = False
            
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
                    self.assets = self.each_trade_amount / price
                    self.last_trade_open_time = timestamp
                elif(self.status == -1):
                    trade_pnl = self.each_trade_amount + self.assets * price
                    trade_pnl -= self.transaction_cost * self.each_trade_amount
                    self.total_transaction_cost += self.transaction_cost * self.each_trade_amount
                    self.net_pnl += trade_pnl
                    self.assets = 0
                    self.total_trades_closed += 1
                    trade_closed = True
                    self.trade_holding_times.append(timestamp - self.last_trade_open_time)
                    if timestamp - self.last_trade_open_time == self.min_time_diff:
                        if trade_pnl > 0:
                            self.immediate_profits += trade_pnl 
                        else:
                            self.immediate_losses += trade_pnl 
                else:
                    print(f"Invalid trade signal at {timestamp}")
                    continue

            if signal == -1:
                if(self.status == 0):
                    self.assets = -self.each_trade_amount / price
                    self.last_trade_open_time = timestamp
                elif(self.status == 1):
                    trade_pnl = self.assets * price - self.each_trade_amount
                    trade_pnl -= self.transaction_cost * self.each_trade_amount
                    self.total_transaction_cost += self.transaction_cost * self.each_trade_amount
                    self.net_pnl += trade_pnl
                    self.assets = 0
                    self.total_trades_closed += 1
                    trade_closed = True
                    self.trade_holding_times.append(timestamp - self.last_trade_open_time)
                    if timestamp - self.last_trade_open_time == self.min_time_diff:
                        if trade_pnl > 0:
                            self.immediate_profits += trade_pnl
                        else:
                            self.immediate_losses += trade_pnl
                else:
                    print(f"Invalid trade signal at {timestamp}")
                    continue

            ## Updating status
            self.status += signal
            if trade_closed:
                self.trade_pnl_lst.append(trade_pnl)
                self.trade_returns.append(trade_pnl + self.transaction_cost * self.each_trade_amount)
                self.annual_trade_returns[str(timestamp.year)].append(trade_pnl + self.transaction_cost * self.each_trade_amount)
                self.logs.loc[row.Index, 'trade_pnl'] = trade_pnl
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

            if(signal != 0):
                # print(f"Trade at {timestamp} with price {price} and signal {signal}, total assets : {self.assets}, trade_pnl : {trade_pnl}, net_pnl : {self.net_pnl}")
                continue
        self.logs['net_pnl'] = self.logs['trade_pnl'].cumsum()
        self.net_pnl_lst = self.logs['net_pnl'].tolist()
        trade_closed = False
        if self.assets > 0:
            trade_pnl = self.assets * close - self.each_trade_amount
            trade_pnl -= self.transaction_cost * self.each_trade_amount
            self.total_transaction_cost += self.transaction_cost * self.each_trade_amount
            self.net_pnl += trade_pnl
            self.assets = 0
            self.trade_pnl_lst.append(trade_pnl)
            self.trade_returns.append(trade_pnl + self.transaction_cost * self.each_trade_amount )
            self.annual_trade_returns[str(timestamp.year)].append(trade_pnl + self.transaction_cost * self.each_trade_amount)
            self.net_pnl_lst.append(self.net_pnl)
            self.total_trades_closed += 1
            self.min_net_pnl = min(self.min_net_pnl, self.net_pnl)
            trade_closed = True
            self.trade_holding_times.append(timestamp - self.last_trade_open_time)
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
            
        elif self.assets < 0:
            trade_pnl = self.each_trade_amount + self.assets * close
            trade_pnl -= self.transaction_cost * self.each_trade_amount
            self.total_transaction_cost += self.transaction_cost * self.each_trade_amount
            self.net_pnl += trade_pnl
            self.assets = 0
            self.trade_pnl_lst.append(trade_pnl)
            self.trade_returns.append(trade_pnl +self.transaction_cost * self.each_trade_amount )
            self.annual_trade_returns[str(timestamp.year)].append(trade_pnl + self.transaction_cost * self.each_trade_amount)
            self.net_pnl_lst.append(self.net_pnl)
            self.total_trades_closed += 1
            self.min_net_pnl = min(self.min_net_pnl, self.net_pnl)
            trade_closed = True
            self.trade_holding_times.append(timestamp - self.last_trade_open_time)
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

    def plot(self) -> None:
        fig, ax = plt.subplots()
        ax.plot(self.net_pnl_lst, label='Net PnL', color='blue')
        ax.axhline(y=0, color='black', linestyle='--')
        ax.set_title("Net PnL and Close Price for Static Approach")
        
        ax.set_xlabel("Time")
        ax.set_ylabel("Net PnL")
        
        ax2 = ax.twinx()
        ax2.plot(self.close_price_lst , label='Close Price', color='orange')
        ax2.axhline(y=0, color='black', linestyle='--')
        ax2.set_ylabel("Close Price")
        
        # Set xtick values using self.logs['datetime']
        len = self.logs.shape[0] - 1
        xticks = [0, len//4, 2*(len//4), 3*(len//4), len]  # Set xticks at the start and end
        ax.set_xticks(xticks)
        ax.set_xticklabels([self.logs.loc[0, 'datetime'], self.logs.loc[len//4, 'datetime'], self.logs.loc[2*(len//4), 'datetime'], self.logs.loc[3*(len//4), 'datetime'], self.logs.loc[len, 'datetime']])  # Set labels at the start and end
            
        # combine the legend entries from all plots
        lines, labels = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax.legend(lines + lines2, labels + labels2, loc='upper left')
        
        # plt.show()
        plt.show()

    def get_metrics(self) -> dict:
        self.metrics["Net PnL"] = self.net_pnl
        self.metrics["Buy and Hold PnL"] = (self.close_price_lst[-1] - self.close_price_lst[0]) * self.each_trade_amount / self.close_price_lst[0]
        self.metrics["Gross Profit"] = self.gross_profit
        self.metrics["Gross Loss"] = self.gross_loss
        self.metrics["Total Trades Closed"] = self.total_trades_closed
        self.metrics["Sharpe Ratio"] = np.mean(np.array(self.trade_pnl_lst))/np.std(np.array(self.trade_pnl_lst))
        self.metrics["Largest Winning Trade"] = self.largest_winning_trade
        self.metrics["Largest Losing Trade"] = self.largest_losing_trade
        self.metrics["Min Net PnL"] = self.min_net_pnl
        self.metrics["Average Winning Trade"] = np.mean(np.array(self.winning_trades_lst))
        self.metrics["Average Losing Trade"] = np.mean(np.array(self.losing_trades_lst))
        self.metrics["Number of Winning Trades"] = self.num_win_trades
        self.metrics["Number of Losing Trades"] = self.num_lose_trades
        self.net_portfolio_lst = np.array(self.net_pnl_lst) + self.each_trade_amount
        # self.metrics["Maximum Drawdown"] = np.max((1 - self.net_portfolio_lst / np.maximum.accumulate(self.net_portfolio_lst)))*100
        self.metrics["Maximum Drawdown"] = max_drawdown(np.array(self.trade_returns)/1000)*100
        self.metrics["Total Transaction Cost"] = self.total_transaction_cost
        self.metrics["Average Trade Holding Duration"] = np.mean([self.trade_holding_times])
        self.metrics["Maximum Trade Holding Duration"] = np.max([self.trade_holding_times])
        self.metrics["Immediate Losses"] = self.immediate_losses
        self.metrics["Immediate Profits"] = self.immediate_profits
        self.metrics["Annual Maximum Drawdowns"] = {}
        self.metrics["Annual Returns"] = {}
        for year, trade_returns in self.annual_trade_returns.items():
            annual_max_drawdown = max_drawdown(np.array(trade_returns)/1000) * 100
            annual_return = sum(trade_returns)
            self.metrics["Annual Maximum Drawdowns"][year] = annual_max_drawdown
            self.metrics["Annual Returns"][year] = (100*annual_return)/1000
        print(f"Maximum Drawdown location : {np.argmax(1 - self.net_portfolio_lst / np.maximum.accumulate(self.net_portfolio_lst))}")
        return self.metrics
    

class Compunding_Engine():
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

            if(signal != 0):
                # print(f"Trade at {timestamp} with price {price} and signal {signal}, total assets : {self.assets}, trade_pnl : {trade_pnl}, net_pnl : {self.net_pnl}, net_cash : {self.cash}")
                continue

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
        plt.title("Net PnL for Compounding Approach")
        plt.xlabel("Time")
        plt.ylabel("Net PnL")
        plt.show()

    def get_metrics(self) -> dict:
        self.metrics["Net PnL"] = self.net_pnl
        self.metrics["Gross Profit"] = self.gross_profit
        self.metrics["Gross Loss"] = self.gross_loss
        self.metrics["Total Trades Closed"] = self.total_trades_closed
        self.metrics["Sharpe Ratio"] = np.mean(np.array(self.daily_pnl_lst))/np.std(np.array(self.daily_pnl_lst))
        self.metrics["Largest Winning Trade"] = self.largest_winning_trade
        self.metrics["Largest Losing Trade"] = self.largest_losing_trade
        self.metrics["Min Net PnL"] = self.min_net_pnl
        self.metrics["Average Winning Trade"] = np.mean(np.array(self.winning_trades_lst))
        self.metrics["Average Losing Trade"] = np.mean(np.array(self.losing_trades_lst))
        self.metrics["Number of Winning Trades"] = self.num_win_trades
        self.metrics["Number of Losing Trades"] = self.num_lose_trades
        self.metrics["Final Cash"] = self.cash
        self.metrics["Total Transaction cost"] = self.total_transaction_cost
        return self.metrics