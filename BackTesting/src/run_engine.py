from main_engine import Static_Engine, Compunding_Engine
import pandas as pd
import sys
import argparse


tstomin = {
    '3m': 3,
    '5m': 5,
    '15m': 15,
    '30m': 30,
    '1h': 60,
}

def generate_results_static(args):
    e = Static_Engine(log_name = args.logs, tick_sz=tstomin[args.ts],  without_transaction_cost=args.wtc)
    df = pd.read_csv(args.logs)
    print(len(df))
    e.add_logs(df)
    e.run()
    metrics = e.get_metrics()
    print("\n" + "*"*60)
    print("*" + " " * 58 + "*")
    print("*" + "Results for Static Method".center(58) + "*")
    print("*" + " " * 58 + "*")
    print("*"*60 + "\n")
    print(metrics['Net PnL'])
    print(f"Net PnL {metrics['Net PnL']}")
    print(f"Buy and Hold PnL {metrics['Buy and Hold PnL']}")
    print(f"Total Trades Closed {metrics['Total Trades Closed']}")
    print(f"Gross Profit {metrics['Gross Profit']}")
    print(f"Gross Loss {metrics['Gross Loss']}")
    print(f"Largest Winning Trade {metrics['Largest Winning Trade']}")
    print(f"Largest Losing Trade {metrics['Largest Losing Trade']}")
    print(f"Sharpe Ratio {metrics['Sharpe Ratio']}")
    print(f"Min Net PnL {metrics['Min Net PnL']}")
    print(f"Average Winning Trade {metrics['Average Winning Trade']}")
    print(f"Average Losing Trade {metrics['Average Losing Trade']}")
    print(f"Number of Winning Trades {metrics['Number of Winning Trades']}")
    print(f"Number of Losing Trades {metrics['Number of Losing Trades']}")
    print(f"Max Drawdown {metrics['Maximum Drawdown']}")
    print(f"Total Transaction Cost {metrics['Total Transaction Cost']}")
    print(f"Maximum Trade Holding Duration {metrics['Maximum Trade Holding Duration']}")
    print(f"Average Trade Holding Duration {metrics['Average Trade Holding Duration']}")
    print(f"Immediate Losses {metrics['Immediate Losses']}" )
    print(f"Immediate Profits {metrics['Immediate Profits']}" )
    print(f"Net PnL {metrics['Net PnL']}")
    print("\nAnnual Returns:")
    for year, annual_return in metrics["Annual Returns"].items():
        print(f"{year}: {annual_return:.2f}%")
    print("\nAnnual Maximum Drawdowns:")
    for year, max_drawdown in metrics["Annual Maximum Drawdowns"].items():
        print(f"{year}: {max_drawdown:.2f}%")
    e.plot()

def generate_results_compounding(args):
    e = Compunding_Engine()
    df = pd.read_csv(args.logs)
    e.add_logs(df)
    e.run()
    metrics = e.get_metrics()
    print("\n" + "*"*60)
    print("*" + " " * 58 + "*")
    print("*" + "Results for Compounding Method".center(58) + "*")
    print("*" + " " * 58 + "*")
    print("*"*60 + "\n")
    print(f"Net PnL {metrics['Net PnL']}")
    print(f"Total Trades Closed {metrics['Total Trades Closed']}")
    print(f"Gross Profit {metrics['Gross Profit']}")
    print(f"Gross Loss {metrics['Gross Loss']}")
    print(f"Largest Winning Trade {metrics['Largest Winning Trade']}")
    print(f"Largest Losing Trade {metrics['Largest Losing Trade']}")
    print(f"Sharpe Ratio {metrics['Sharpe Ratio']}")
    print(f"Min Net PnL {metrics['Min Net PnL']}")
    print(f"Average Winning Trade {metrics['Average Winning Trade']}")
    print(f"Average Losing Trade {metrics['Average Losing Trade']}")
    print(f"Number of Winning Trades {metrics['Number of Winning Trades']}")
    print(f"Number of Losing Trades {metrics['Number of Losing Trades']}")
    print(f"Final Cash {metrics['Final Cash']}")
    print(f"Total Transaction Cost {metrics['Total Transaction cost']}")
    e.plot()

def run_method(args):
    methods = {
        'both': lambda: [generate_results_static(args), generate_results_compounding(args)],
        'static': lambda: generate_results_static(args),
        'compounding': lambda: generate_results_compounding(args)
    }

    method_function = methods.get(args.method, lambda: None)
    return method_function()


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--logs", help="path to logs file", required=True)
    parser.add_argument('--wtc', action='store_true', help='without transaction cost')
    parser.add_argument('--ts', help='tick size eg. 3m/5m/15m/30m/1h', required=True)
    parser.add_argument('--method',help='static, compounding or both', default='static')
    args = parser.parse_args()
    run_method(args)