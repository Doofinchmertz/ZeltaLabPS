import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
import numpy as np



df = pd.read_csv('data/btc_1h_train.csv')

y = df.filter(like = 'target')
X = df.drop(y.columns, axis=1)
X = X.drop(['open', 'high', 'low', 'close'], axis=1)
X = X.drop('datetime', axis=1)

scaler = StandardScaler()
X_normalized = scaler.fit_transform(X)
X = pd.DataFrame(X_normalized, columns=X.columns)
y = pd.DataFrame(y, columns=y.columns)


model = Ridge(alpha=0.01)
look_back = 1920
pred_window = 72
target_k = 1
sl_thresh = 4
y_pred = []
y_actual = []
df['predicted_return'] = 0
for i in range(look_back, len(X) - pred_window, pred_window):
    model.fit(X[i-look_back:i-target_k], y[i-look_back:i-target_k][f'target_{target_k}d'])
    df.loc[df[i:i+pred_window].index, 'predicted_return'] = model.predict(X[i:i+pred_window])

df.drop(df.index[:look_back], inplace=True)
cut = 1.5
df['indicator'] = np.where(df['predicted_return'] > cut, 1, np.where(df['predicted_return'] < -cut, -1, 0))

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
df.to_csv(f"../src/logs/rolling_lr_with_sl.csv")

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
# df.to_csv(f"../src/logs/rolling_lr_with_sl.csv")