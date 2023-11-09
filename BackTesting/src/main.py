from engine import Engine
import pandas as pd
import sys
import argparse

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--logs", help = "path to logs file", required = True)    
    args = parser.parse_args()

    # e = Engine()
    df = pd.read_csv(args.logs)
    print(df.columns)
    # e.add_logs(df)
    # e.run()
    # metrics = e.get_metrics()
    # print(f"Metrics : {metrics}")
    # e.logs.to_csv("updates_logs.csv")
    # e.plot()