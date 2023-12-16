from engine_compounding import Engine
import pandas as pd
import sys
import argparse

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--logs", help = "path to logs file", required = True)    
    args = parser.parse_args()

    e = Engine()
    df = pd.read_csv(args.logs)
    e.add_logs(df)
    e.run()
    metrics = e.get_metrics()
    print(metrics['Net PnL'])
    # print(f"Net PnL {metrics['Net PnL']}")
    # print(f"Total Trades Closed {metrics['Total Trades Closed']}")
    # print(f"Gross Profit {metrics['Gross Profit']}")
    # print(f"Gross Loss {metrics['Gross Loss']}")
    # print(f"Largest Winning Trade {metrics['Largest Winning Trade']}")
    # print(f"Largest Losing Trade {metrics['Largest Losing Trade']}")
    # print(f"Sharpe Ratio {metrics['Sharpe Ratio']}")
    # print(f"Min Net PnL {metrics['Min Net PnL']}")
    # print(f"Average Winning Trade {metrics['Average Winning Trade']}")
    # print(f"Average Losing Trade {metrics['Average Losing Trade']}")
    # print(f"Number of Winning Trades {metrics['Number of Winning Trades']}")
    # print(f"Number of Losing Trades {metrics['Number of Losing Trades']}")
    # print(f"Final Cash {metrics['Final Cash']}")
    # print(f"Total Transaction Cost {metrics['Total Transaction cost']}")
    # e.plot()