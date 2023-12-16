from sklearn.linear_model import LinearRegression, Lasso
import pandas as pd
import sys
import numpy as np
import warnings
warnings.filterwarnings('ignore')

k = sys.argv[2]

def read_file(filename):
    return pd.read_csv(filename, index_col=0, parse_dates=True, infer_datetime_format=True)

def get_data(timeframe, name):
    return read_file("data_with_new_indicators/btcusdt_" + timeframe + "_" + name + ".csv")

# Tick Size of Data
time_frame = sys.argv[1]

# Load data
df_train = get_data(time_frame, "total")
df_val = get_data(time_frame, "complete")


# Create the linear regression model
model = LinearRegression()


# Define the independent variables
X_train = df_train.drop(f'Next_{k}_Days_Return', axis=1)
X_train1 = X_train.drop('open', axis=1)
X_train1 = X_train1.drop('close', axis=1)

X_val = df_val.drop(f'Next_{k}_Days_Return', axis=1)
X_val1 = X_val.drop('open', axis=1)
X_val1 = X_val1.drop('close', axis=1)

# Define the dependent variable
y_train = df_train[f'Next_{k}_Days_Return']
y_val = df_val[f'Next_{k}_Days_Return']


df_train['indicator'] = 0


model.fit(X_train1, y_train)
print("model_coef", model.coef_)


# Predict the dependent variable of the totaling data
y_pred = model.predict(X_train1)
quantile_value = np.quantile(np.abs(y_pred), 0.90)
print("quantile value: ", quantile_value)
print(np.corrcoef(y_pred, y_train)[0,1])
# y_pred = model.predict(X_train)
# quantile_value = 1.5


# df_train['flag'] = np.where(y_pred > quantile_value, 1, np.where(y_pred < -quantile_value, -1, 0))
# df = df_train

# df['logs'] = np.nan

# disable_trading = 0
# stop_loss = 0
# compare = 0
# thresh = -0.02
# for i in range(len(df)):
#     if df["flag"].iloc[i] == 1 and compare == 0:
#         # No open trade, encouter buy singal
#         stop_loss = 0
#         buy_price = df["close"].iloc[i]
        
#         compare = 1
#         df["logs"].iloc[i] = 1


#     elif (df["flag"].iloc[i] != -1 and compare == 1):
#         # Current buy trade, encounter buy signal or no signal - do nothing, update stop loss
#         df["logs"].iloc[i] = 0

#         #calculate pnl, if we exit now
#         sell_price = df["close"].iloc[i]
#         exit_loss = (sell_price - buy_price)/buy_price 
#         stop_loss = min(stop_loss, exit_loss)

#         #exit trade, if the loss is higher than stop loss
#         if stop_loss < thresh and disable_trading == 0:
#             df["logs"].iloc[i] = -1
#             # print(f"disable_trading in buy trade - stop loss: {disable_trading}")
#             disable_trading = 1


#     elif df["flag"].iloc[i] == -1 and compare == 1:
#         # Current buy trade, encounter sell signal

#         #exit trade
#         df["logs"].iloc[i] = -1
#         compare = 0
#         stop_loss = 0

#         #if trade was already exited before, check for disable trading flag here, do nothing here
#         if disable_trading == 1:
#             disable_trading = 0
#             # print(f"disable_trading in buy trade - while exiting: {disable_trading}")
#             df["logs"].iloc[i] = 0



#     elif df["flag"].iloc[i] == -1 and compare == 0:
#         # No close trade, enounter sell siganl 
#         stop_loss = 0
#         sell_price = df["close"].iloc[i]
        
#         compare = -1
#         df["logs"].iloc[i] = -1


#     elif (df["flag"].iloc[i] != 1 and compare == -1):
#         # Current sell trade, encounter sell signal or no signal - do nothing, update stop loss
#         df["logs"].iloc[i] = 0

#         #calculate pnl, if we exit now
#         buy_price = df["close"].iloc[i]
#         exit_loss = (sell_price - buy_price)/sell_price 
#         stop_loss = min(stop_loss, exit_loss)

#         #exit trade, if the loss is higher than stop loss
#         if stop_loss < thresh and disable_trading == 0:
#             df["logs"].iloc[i] = 1
#             # print(f"disable_trading in sell trade - stop loss: {disable_trading}")
#             # print(i)
#             disable_trading = 1

#     elif df["flag"].iloc[i] == 1 and compare == -1:
#         # 
#         # print("Current sell trade, encounter buy signal")
#         # print(f"{disable_trading}")

#         #exit trade
#         df["logs"].iloc[i] = 1
#         compare = 0
#         stop_loss = 0

#         #if trade was already exited before, check for disable trading flag here, do nothing here
#         if disable_trading == 1:
#             # print("Check")
#             disable_trading = 0
#             df["logs"].iloc[i] = 0

#     elif df["flag"].iloc[i] == 0 and compare == 0:
#         df["logs"].iloc[i] == 0


df_train['indicator'] = np.where(y_pred > quantile_value, 1, np.where(y_pred < -quantile_value, -1, 0))
data = df_train
tot = 0
for index, _ in data.iterrows():
    data.at[index, 'signal'] = 0
    if data.at[index, 'indicator'] == 1:
        if tot == 0 or tot == -1:
            # enter long position/exit short position
            tot += 1
            data.at[index, 'signal'] = 1
    elif data.at[index, 'indicator'] == -1:
        if tot == 0 or tot == 1:
            # enter short position/exit long position
            tot -= 1
            data.at[index, 'signal'] = -1
    else:
        if tot == 1:
            # exit long position
            data.at[index, 'signal'] = -1
        elif tot == -1:
            # exit short position
            data.at[index, 'signal'] = 1
        tot = 0
data.to_csv("../src/logs/lin_reg_train_" + time_frame + ".csv")



# Fill in any missing values in the new column with 0.
# df['logs'].fillna(0, inplace=True)

# #close out positions (if needed)

# df["logs"].iloc[-1] = -np.sum(df["logs"])


# df.rename(columns={"logs": "signal"}, inplace=True)
# df.to_csv("../src/logs/lin_reg_train_" + time_frame + ".csv")
# data.to_csv("../src/logs/lin_reg_total_" + time_frame + ".csv")





# Predict the dependent variable of the totaling data
y_pred = model.predict(X_val1)
# quantile_value = np.quantile(np.abs(y_pred), 0.99)
# print("quantile value: ", quantile_value)
print(np.corrcoef(y_pred, y_val)[0,1])
# quantile_value = 1.5


# df_val['flag'] = np.where(y_pred > quantile_value, 1, np.where(y_pred < -quantile_value, -1, 0))
# df = df_val

# df['logs'] = np.nan

# disable_trading = 0
# stop_loss = 0
# compare = 0
# thresh = -0.02
# for i in range(len(df)):
#     if df["flag"].iloc[i] == 1 and compare == 0:
#         # No open trade, encouter buy singal
#         stop_loss = 0
#         buy_price = df["close"].iloc[i]
        
#         compare = 1
#         df["logs"].iloc[i] = 1


#     elif (df["flag"].iloc[i] != -1 and compare == 1):
#         # Current buy trade, encounter buy signal or no signal - do nothing, update stop loss
#         df["logs"].iloc[i] = 0

#         #calculate pnl, if we exit now
#         sell_price = df["close"].iloc[i]
#         exit_loss = (sell_price - buy_price)/buy_price 
#         stop_loss = min(stop_loss, exit_loss)

#         #exit trade, if the loss is higher than stop loss
#         if stop_loss < thresh and disable_trading == 0:
#             df["logs"].iloc[i] = -1
#             # print(f"disable_trading in buy trade - stop loss: {disable_trading}")
#             disable_trading = 1


#     elif df["flag"].iloc[i] == -1 and compare == 1:
#         # Current buy trade, encounter sell signal

#         #exit trade
#         df["logs"].iloc[i] = -1
#         compare = 0
#         stop_loss = 0

#         #if trade was already exited before, check for disable trading flag here, do nothing here
#         if disable_trading == 1:
#             disable_trading = 0
#             # print(f"disable_trading in buy trade - while exiting: {disable_trading}")
#             df["logs"].iloc[i] = 0



#     elif df["flag"].iloc[i] == -1 and compare == 0:
#         # No close trade, enounter sell siganl 
#         stop_loss = 0
#         sell_price = df["close"].iloc[i]
        
#         compare = -1
#         df["logs"].iloc[i] = -1


#     elif (df["flag"].iloc[i] != 1 and compare == -1):
#         # Current sell trade, encounter sell signal or no signal - do nothing, update stop loss
#         df["logs"].iloc[i] = 0

#         #calculate pnl, if we exit now
#         buy_price = df["close"].iloc[i]
#         exit_loss = (sell_price - buy_price)/sell_price 
#         stop_loss = min(stop_loss, exit_loss)

#         #exit trade, if the loss is higher than stop loss
#         if stop_loss < thresh and disable_trading == 0:
#             df["logs"].iloc[i] = 1
#             # print(f"disable_trading in sell trade - stop loss: {disable_trading}")
#             # print(i)
#             disable_trading = 1

#     elif df["flag"].iloc[i] == 1 and compare == -1:
#         # 
#         # print("Current sell trade, encounter buy signal")
#         # print(f"{disable_trading}")

#         #exit trade
#         df["logs"].iloc[i] = 1
#         compare = 0
#         stop_loss = 0

#         #if trade was already exited before, check for disable trading flag here, do nothing here
#         if disable_trading == 1:
#             # print("Check")
#             disable_trading = 0
#             df["logs"].iloc[i] = 0

#     elif df["flag"].iloc[i] == 0 and compare == 0:
#         df["logs"].iloc[i] == 0


# # Fill in any missing values in the new column with 0.
# df['logs'].fillna(0, inplace=True)

# #close out positions (if needed)

# df["logs"].iloc[-1] = -np.sum(df["logs"])


# df.rename(columns={"logs": "signal"}, inplace=True)
# df.to_csv("../src/logs/lin_reg_val_" + time_frame + ".csv")


df_val['indicator'] = np.where(y_pred > quantile_value, 1, np.where(y_pred < -quantile_value, -1, 0))
data = df_val
tot = 0
for index, _ in data.iterrows():
    data.at[index, 'signal'] = 0
    if data.at[index, 'indicator'] == 1:
        if tot == 0 or tot == -1:
            # enter long position/exit short position
            tot += 1
            data.at[index, 'signal'] = 1
    elif data.at[index, 'indicator'] == -1:
        if tot == 0 or tot == 1:
            # enter short position/exit long position
            tot -= 1
            data.at[index, 'signal'] = -1
    else:
        if tot == 1:
            # exit long position
            data.at[index, 'signal'] = -1
        elif tot == -1:
            # exit short position
            data.at[index, 'signal'] = 1
        tot = 0
data.to_csv("../src/logs/lin_reg_val_" + time_frame + ".csv")
