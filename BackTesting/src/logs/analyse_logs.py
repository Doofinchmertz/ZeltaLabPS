import pandas as pd
# -1,1

df = pd.read_csv("lin_reg_test_5m.csv")

## Checking is stoploss matters?
df_trades = df[df["logs"] != 0]
index = df_trades.index.to_list()

#just examining buy trades for now (when we lose money vs when we win money)
returns_all = []
returns_low_all = []
trades = []
for i in range(0, len(df_trades), 2):
    prices = df["open"][index[i]: index[i+1]]

    if df["logs"].iloc[index[i]] == 1:
        buy_price = df["open"].iloc[index[i]]
        sell_price = df["open"].iloc[index[i+1]]
        
        if len(prices) > 2:
            returns = (sell_price - buy_price)/buy_price
            returns_all.append(returns)
            low = min(prices[:-1])
            returns_low = (low - buy_price)/buy_price
            returns_low_all.append(returns_low)
            trades.append("long")

    elif df["logs"].iloc[index[i]] == -1:
        sell_price = df["open"].iloc[index[i]]
        buy_price = df["open"].iloc[index[i+1]]

        if len(prices) > 2:
            returns = (sell_price - buy_price)/sell_price
            returns_all.append(returns)
            high = max(prices[:-1])
            returns_low = (sell_price - high)/sell_price
            returns_low_all.append(returns_low)
            trades.append("short")


colors = ['red', 'blue']

plt.figure(figsize=(12,8))
# Create a scatter plot and color code the points based on the labels
for j,trade in enumerate(set(trades)):
    print(trade)
    x_group = [returns_all[i] for i in range(len(returns_all)) if trades[i] == trade]
    y_group = [returns_low_all[i] for i in range(len(returns_all)) if trades[i] == trade]
    color = colors[j]
    plt.scatter(x_group, y_group, label=f'{trade}', c=color)


plt.legend()
plt.grid(True)