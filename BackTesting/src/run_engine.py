from main_engine import Static_Engine, Compounding_Engine
import pandas as pd
import argparse

def print_metrics(metrics):
    print(f"Net PnL {metrics['Net PnL']}")
    print(f"Buy and Hold PnL {metrics['Buy and Hold PnL']}")
    print(f"Total Trades Closed {metrics['Total Trades Closed']}")
    print(f"Gross Profit {metrics['Gross Profit']}")
    print(f"Gross Loss {metrics['Gross Loss']}")
    print(f"Largest Winning Trade {metrics['Largest Winning Trade']}")
    print(f"Largest Losing Trade {metrics['Largest Losing Trade']}")
    print(f"Min Net PnL {metrics['Min Net PnL']}")
    print(f"Sharpe Ratio {metrics['Sharpe Ratio']}")
    print(f"Average Winning Trade {metrics['Average Winning Trade']}")
    print(f"Average Losing Trade {metrics['Average Losing Trade']}")
    print(f"Number of Winning Trades {metrics['Number of Winning Trades']}")
    print(f"Number of Losing Trades {metrics['Number of Losing Trades']}")
    print(f"Total Transaction Cost {metrics['Total Transaction Cost']}")
    print(f"Max Drawdown {metrics['Maximum Drawdown']}")
    print(f"Maximum Trade Holding Duration {metrics['Maximum Trade Holding Duration']}")
    print(f"Average Trade Holding Duration {metrics['Average Trade Holding Duration']}")
    print("\nAnnual Returns:")
    for year, annual_return in metrics["Annual Returns"].items():
        print(f"{year}: {annual_return:.2f}%")
    print("\nAnnual Maximum Drawdowns:")
    for year, max_drawdown in metrics["Annual Maximum Drawdowns"].items():
        print(f"{year}: {max_drawdown:.2f}%")

def generate_results_static(args):
    # Make instance of static engine, add logs, run, get metrics and plot
    e = Static_Engine(without_transaction_cost=args.wtc)
    df = pd.read_csv(args.logs)
    e.add_logs(df)
    e.run()
    metrics = e.get_metrics()
    print("\n" + "*"*60)
    print("*" + " " * 58 + "*")
    print("*" + "Results for Static Method".center(58) + "*")
    print("*" + " " * 58 + "*")
    print("*"*60 + "\n")
    print_metrics(metrics)
    e.plot()

def generate_results_compounding(args):
    # Make instance of compounding engine, add logs, run, get metrics and plot
    e = Compounding_Engine()
    df = pd.read_csv(args.logs)
    e.add_logs(df)
    e.run()
    metrics = e.get_metrics()
    print("\n" + "*"*60)
    print("*" + " " * 58 + "*")
    print("*" + "Results for Compounding Method".center(58) + "*")
    print("*" + " " * 58 + "*")
    print("*"*60 + "\n")
    print_metrics(metrics)
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
    parser.add_argument('--method',help='static, compounding or both', default='static')
    args = parser.parse_args()
    run_method(args)