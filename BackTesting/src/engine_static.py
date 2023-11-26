import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import os

class Engine():
    def __init__(self, static_trade_amount = 1000, gen_vis_logs = False) -> None:
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
        self.metrics_logs = pd.DataFrame(columns=['Trade PnL', 'Net PnL'])
        self.gen_vis_logs = gen_vis_logs
        self.assets = 0
        self.open_price_lst = []
        self.close_price_lst = []

    def add_logs(self, logs: pd.DataFrame) -> None:
        self.logs = logs

    def run(self) -> None:
        for row in self.logs.itertuples():
            signal = int(row.signal)
            timestamp = row.datetime
            close = row.close
            open = row.open
            price = close
            trade_closed = False
            self.open_price_lst.append(open)
            self.close_price_lst.append(close)

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
                elif(self.status == -1):
                    trade_pnl = self.each_trade_amount + self.assets * price
                    self.net_pnl += trade_pnl
                    self.assets = 0
                    self.total_trades_closed += 1
                    trade_closed = True
                else:
                    print(f"Invalid trade signal at {timestamp}")
                    continue

            if signal == -1:
                if(self.status == 0):
                    self.assets = -self.each_trade_amount / price
                elif(self.status == 1):
                    trade_pnl = self.assets * price - self.each_trade_amount
                    self.net_pnl += trade_pnl
                    self.assets = 0
                    self.total_trades_closed += 1
                    trade_closed = True
                else:
                    print(f"Invalid trade signal at {timestamp}")
                    continue

            ## Updating status
            self.status += signal
            if trade_closed:
                self.trade_pnl_lst.append(trade_pnl)
            self.net_pnl_lst.append(self.net_pnl)
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
            if self.gen_vis_logs:
                self.metrics_logs = pd.concat([self.metrics_logs,pd.DataFrame({'Trade PnL': [trade_pnl], 'Net PnL': [self.net_pnl]})], ignore_index=True)

            if(signal != 0):
                print(f"Trade at {timestamp} with price {price} and signal {signal}, total assets : {self.assets}, trade_pnl : {trade_pnl}, net_pnl : {self.net_pnl}")

        if self.assets > 0:
            trade_pnl = self.assets * close - self.each_trade_amount
            self.net_pnl += trade_pnl
            self.assets = 0
            self.trade_pnl_lst.append(trade_pnl)
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
            
        elif self.assets < 0:
            trade_pnl = self.each_trade_amount + self.assets * close
            self.net_pnl += trade_pnl
            self.assets = 0
            self.trade_pnl_lst.append(trade_pnl)
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
        if self.gen_vis_logs:
            self.metrics_logs = pd.concat([self.metrics_logs,pd.DataFrame({'Trade PnL': [trade_pnl], 'Net PnL': [self.net_pnl]})], ignore_index=True)

    def plot(self)-> None:
        fig, ax = plt.subplots()
        ax.plot(self.net_pnl_lst, label='Net PnL')
        ax.axhline(y=0, color='black', linestyle='--')
        ax.set_title("Net PnL and Open Price")
        ax.set_xlabel("Time")
        ax.set_ylabel("Net PnL")
        
        ax2 = ax.twinx()
        ax2.plot(self.close_price_lst, label='Open Price', color='orange')
        ax2.axhline(y=0, color='black', linestyle='--')
        ax2.set_ylabel("Open Price")
        
        # combine the legend entries from both plots
        lines, labels = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax.legend(lines + lines2, labels + labels2, loc='upper left')
        
        plt.show()

    def get_metrics(self) -> dict:
        if self.gen_vis_logs:
            if not os.path.exists("metric_logs"):
                os.makedirs("metric_logs")
            self.metrics_logs.to_csv("metric_logs/static_metric_logs.csv")
        self.metrics["Net PnL"] = self.net_pnl
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
        self.metrics["Maximum Drawdown"] = np.max((1 - self.net_portfolio_lst / np.maximum.accumulate(self.net_portfolio_lst)))*100
        print(f"Maximum Drawdown location : {np.argmax(1 - self.net_portfolio_lst / np.maximum.accumulate(self.net_portfolio_lst))}")
        return self.metrics