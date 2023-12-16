import argparse
import pandas as pd

# Create the argument parser
parser = argparse.ArgumentParser()

# Add the --logs argument
parser.add_argument("--logs", help="Location of the logs file")

# Parse the command line arguments
args = parser.parse_args()

# Access the value of the --logs argument
logs_location = args.logs

# Use the logs_location variable in your code
df = pd.read_csv(logs_location)

assets = 0
status = 0
each_trade_amount = 1000
transaction_cost = 0.0015
net_pnl = 0
theoretical_net_pnl = 0
max_net_pnl = 0
allowed_drawdown = 0.1
flag = False

for i in range(len(df)):
    signal = df.iloc[i]['signal']
    trade_pnl = 0
    price = df.iloc[i]['close']
    if signal == 1:
        if status == 0:
            assets = each_trade_amount/price
            status = 1
        elif status == -1:
            trade_pnl = each_trade_amount + assets*price
            trade_pnl -= transaction_cost*each_trade_amount
            if not flag:
                net_pnl += trade_pnl
            theoretical_net_pnl += trade_pnl
            assets = 0
            status = 0
    if signal == -1:
        if status == 0:
            assets = -each_trade_amount/price
            status = -1
        elif status == 1:
            trade_pnl = assets*price - each_trade_amount
            trade_pnl -= transaction_cost*each_trade_amount
            if not flag:
                net_pnl += trade_pnl
            theoretical_net_pnl += trade_pnl
            assets = 0
            status = 0
    if flag:
        df.at[i, 'signal'] = 0
    # print(net_pnl)
    if theoretical_net_pnl >= max_net_pnl:
        max_net_pnl = theoretical_net_pnl
        flag = False
    else:
        if theoretical_net_pnl<(1-allowed_drawdown)*max_net_pnl:
            flag = True
        else:
            flag = False

print(net_pnl)
print(theoretical_net_pnl)

df.to_csv('logs/output1.csv', index=False)
