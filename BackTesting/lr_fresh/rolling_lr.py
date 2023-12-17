import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np

df = pd.read_csv("data/btcusdt_1h_diamond.csv")
df['datetime'] = pd.to_datetime(df['datetime'])
df.set_index(df['datetime'], inplace=True)

y = df['Next_2h_Return']
X = df.drop(['Next_2h_Return', 'open', 'close', 'datetime', 'volume', 'high', 'low'], axis=1)

look_back = 1248
pred_window = 1056
k = 2
cut = 2.5
lamda = 0.8

old_coef = np.zeros(X.shape[1])
old_intercept = 0
df['predicted_return'] = 0
model = LinearRegression()
for i in range(look_back, len(X) - pred_window, pred_window):
    # lower_quantile = y[i-look_back:i-k].quantile(0.001)
    # upper_quantile = y[i-look_back:i-k].quantile(0.999)
    # X_merged = pd.concat([X[i-look_back:i-k], y[i-look_back:i-k]], axis=1)
    # X_merged = X_merged[(X_merged['Next_2h_Return'] > lower_quantile) & (X_merged['Next_2h_Return'] < upper_quantile)]
    # model.fit(X_merged.drop('Next_2h_Return', axis=1), X_merged['Next_2h_Return'])
    model.fit(X[i-look_back:i-k], y[i-look_back:i-k])
    # new_coef = model.coef_
    # new_intercept = model.intercept_
    # model.coef_ = lamda * new_coef + (1 - lamda) * old_coef
    # model.intercept_ = lamda * new_intercept + (1 - lamda) * old_intercept
    # old_coef = model.coef_
    # old_intercept = model.intercept_
    df.loc[df[i:i+pred_window].index, 'predicted_return'] = model.predict(X[i:i+pred_window])
df.drop(df.index[:look_back], inplace=True)
df['indicator'] = np.where(df['predicted_return'] > cut, 1, np.where(df['predicted_return'] < -cut, -1, 0))
df['signal'] = 0

# Without Stoploss
tot = 0
for index, _ in df.iterrows():
    df.at[index, 'signal'] = 0
    if df.at[index, 'indicator'] == 1:
        if tot == 0 or tot == -1:
            # enter long position/exit short position
            tot += 1
            df.at[index, 'signal'] = 1
    elif df.at[index, 'indicator'] == -1:
        if tot == 0 or tot == 1:
            # enter short position/exit long position
            tot -= 1
            df.at[index, 'signal'] = -1
df.to_csv(f"../src/logs/rolling_lr.csv")

# ## With Stoploss
# sl_thresh = 20
# compare = 0
# thresh = -0.01*sl_thresh
# disable_trading = 0
# logs = []
# for i in range(len(df)):
#     if df['indicator'].iloc[i] == 1 and compare == 0:
#         # No open trade, enounter buy siganl 
#         exit_loss = 0
#         buy_price = df["close"].iloc[i]
#         compare = 1
#         logs.append(1)
#     elif (df['indicator'].iloc[i] != -1 and compare == 1):
#         # Current buy trade, encounter buy signal or no signal - do nothing, update stop loss
#         logs.append(0)
#         #calculate pnl, if we exit now
#         sell_price = df["close"].iloc[i]
#         exit_loss = (sell_price - buy_price)/sell_price 
#         #exit trade, if the loss is higher than stop loss
#         if exit_loss < thresh and disable_trading == 0:
#             logs[-1] = -1
#             disable_trading = 1
#     elif df['indicator'].iloc[i] == -1 and compare == 1:
#         # exit trade
#         logs.append(-1)
#         compare = 0
#         exit_loss = 0
#         #if trade was already exited before, check for disable trading flag here, do nothing here
#         if disable_trading == 1:
#             disable_trading = 0
#             logs[-1] = 0
    
#     #SHORT TRADES
#     elif df['indicator'].iloc[i] == -1 and compare == 0:
#         # No open trade, enounter sell siganl 
#         exit_loss = 0
#         sell_price = df["close"].iloc[i]
#         compare = -1
#         logs.append(-1)
    
#     elif (df['indicator'].iloc[i] != 1 and compare == -1):
#         # Current sell trade, encounter sell signal or no signal - do nothing, update stop loss
#         logs.append(0)
#         #calculate pnl, if we exit now
#         buy_price = df["close"].iloc[i]
#         exit_loss = (sell_price - buy_price)/sell_price 
#         #exit trade, if the loss is higher than stop loss
#         if exit_loss < thresh and disable_trading == 0:
#             logs[-1] = 1
#             disable_trading = 1
    
#     elif df['indicator'].iloc[i] == 1 and compare == -1:
#         # exit trade
#         logs.append(1)
#         compare = 0
#         exit_loss = 0
#         #if trade was already exited before, check for disable trading flag here, do nothing here
#         if disable_trading == 1:
#             disable_trading = 0
#             logs[-1] = 0
    
#     elif df['indicator'].iloc[i] == 0 and compare == 0:
#         logs.append(0)

# logs[-1] = -np.sum(logs)
# df['signal'] = np.array(logs)

# df = df[['datetime', 'open', 'high', 'low', 'close', 'signal']]
# df.to_csv(f"../src/logs/rolling_lr.csv")