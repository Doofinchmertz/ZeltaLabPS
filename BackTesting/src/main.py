from engine import Engine
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
    print(f"Gross Profit {metrics['Gross Profit']}")
    print(f"Net Profit {metrics['Net Profit']}")
    print(f"Total Trades Closed {metrics['Total Trades Closed']}")
    print(f"Strategy PnL {metrics['Strategy_PnL']}")
    print(f"Buy and Hold PnL {metrics['Buy and Hold PnL']}")
    print(f"Gross Loss {metrics['Gross Loss']}")
    print(f"Max Drawdown {metrics['Max Drawdown']}")
    print(f"Sharpe Ratio {metrics['Sharpe Ratio']}")
    e.plot()