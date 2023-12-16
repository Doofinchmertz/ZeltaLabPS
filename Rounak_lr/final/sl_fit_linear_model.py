from sklearn.linear_model import LinearRegression, Ridge, Lasso
import pandas as pd
import sys
import numpy as np


k = sys.argv[2]


def read_file(filename):
    return pd.read_csv(filename, index_col=0, parse_dates=True, infer_datetime_format=True)


def get_data(timeframe, name):
    return read_file("data_with_new_indicators/btcusdt_" + timeframe + "_" + name + ".csv")


# Tick Size of Data
time_frame = sys.argv[1]
# Load data
df_train = get_data(time_frame, "train")
df_val = get_data(time_frame, "val")


# Create the linear regression model
model = LinearRegression()


# Define the independent variables
X_train = df_train.drop(f'Next_{k}_Days_Return', axis=1)
X_train = X_train.drop('open', axis=1)
X_train = X_train.drop('close', axis=1)
X_val = df_val.drop(f'Next_{k}_Days_Return', axis=1)
X_val = X_val.drop('open', axis=1)
X_val = X_val.drop('close', axis=1)


# Define the dependent variable
y_train = df_train[f'Next_{k}_Days_Return']
y_val = df_val[f'Next_{k}_Days_Return']
# print(X_train.shape, y_train.shape)
# print(X_val.shape, y_val.shape)


df_train['indicator'] = 0
df_val['indicator'] = 0
# Fit the linear regression model on the training data


model.fit(X_train, y_train)
print("model_coef", model.coef_)


# Predict the dependent variable of the training data
y_pred = model.predict(X_train)
quantile_value = np.quantile(np.abs(y_pred), 0.93)
print("quantile value: ", quantile_value)
print(np.corrcoef(y_pred, y_train)[0,1])
quantile_value = 1.6
# print(df_train['datetime'].head())
df_train['date_time'] = list(pd.to_datetime(pd.Series(df_train.index)))
df_val['date_time'] = list(pd.to_datetime(pd.Series(df_val.index)))


df_train['flag'] = np.where(y_pred > quantile_value, 1, np.where(y_pred < -quantile_value, -1, 0))
df_fine = pd.read_csv("data_with_new_indicators/btcusdt_3m_train.csv")
df_train = df_train.drop(columns= ["open", "close", "volume"])
df_fine["datetime"] = pd.to_datetime(df_fine["datetime"])
df_fine.rename(columns={'datetime': 'date_time'}, inplace=True)
df_train = df_fine.merge(df_train[['date_time', 'flag']], on='date_time', how='left')
df_train.fillna(0, inplace=True)
# print(df_train.head())
exit_loss = 0
disable_trading = 0
# stop_loss = 0
compare = 0
thresh = -0.10
logs = []
for i in range(len(df_train)):
    if df_train["flag"].iloc[i] == 1 and compare == 0:
        # No open trade, encouter buy singal
        exit_loss = 0
        buy_price = df_train["close"].iloc[i]
        
        compare = 1
        logs.append(1)

    #Once we close a trade, we have to check in df_fine whether to exit or not

    elif (df_train["flag"].iloc[i] != -1 and compare == 1):
        # Current buy trade, encounter buy signal or no signal - do nothing, update stop loss
        logs.append(0)

        #calculate pnl, if we exit now
        sell_price = df_train["close"].iloc[i]
        exit_loss = (sell_price - buy_price)/buy_price 
        

        #exit trade, if the loss is higher than stop loss
        if exit_loss < thresh and disable_trading == 0:
            logs[-1] = -1
            # print(f"disable_trading in buy trade - stop loss: {disable_trading}")
            disable_trading = 1


    elif df_train["flag"].iloc[i] == -1 and compare == 1:
        # Current buy trade, encounter sell signal

        #exit trade
        logs.append(-1)
        compare = 0
        exit_loss = 0

        #if trade was already exited before, check for disable trading flag here, do nothing here
        if disable_trading == 1:
            disable_trading = 0
            # compare = -1
            # print(f"disable_trading in buy trade - while exiting: {disable_trading}")
            logs[-1] = 0


    #SHORT TRADES
    elif df_train["flag"].iloc[i] == -1 and compare == 0:
        # No close trade, enounter sell siganl 
        exit_loss = 0
        sell_price = df_train["close"].iloc[i]
        
        compare = -1
        logs.append(-1)


    elif (df_train["flag"].iloc[i] != 1 and compare == -1):
        # Current sell trade, encounter sell signal or no signal - do nothing, update stop loss
        logs.append(0)

        #calculate pnl, if we exit now
        buy_price = df_train["close"].iloc[i]
        exit_loss = (sell_price - buy_price)/sell_price 
    

        #exit trade, if the loss is higher than stop loss
        if exit_loss < thresh and disable_trading == 0:
            logs[-1] = 1
            # print(f"disable_trading in sell trade - stop loss: {disable_trading}")
            # print(i)
            disable_trading = 1

    elif df_train["flag"].iloc[i] == 1 and compare == -1:
        # 
        # print("Current sell trade, encounter buy signal")
        # print(f"{disable_trading}")

        #exit trade
        logs.append(1)
        compare = 0
        exit_loss = 0

        #if trade was already exited before, check for disable trading flag here, do nothing here
        if disable_trading == 1:
            # print("Check")
            disable_trading = 0
            logs[-1] = 0
            # compare = 1

    elif df_train["flag"].iloc[i] == 0 and compare == 0:
        logs.append(0)

#close out positions (if needed)
logs[-1] = -np.sum(logs)

df_train["logs"] = np.array(logs)

# rename column logs to signal
df_train.rename(columns={'logs': 'signal'}, inplace=True)
df_train.rename(columns={'date_time': 'datetime'}, inplace=True)

print(df_train[df_train['signal'] != 0])

df_train.to_csv("../src/logs/lin_reg_train_" + time_frame + ".csv")


# Predict the dependent variable of the validation data
y_pred = model.predict(X_val)
print(np.corrcoef(y_pred, y_val)[0,1])


df_val['flag'] = np.where(y_pred > quantile_value, 1, np.where(y_pred < -quantile_value, -1, 0))
exit_loss = 0
disable_trading = 0
# stop_loss = 0
compare = 0
thresh = -0.08
logs = []
for i in range(len(df_val)):
    if df_val["flag"].iloc[i] == 1 and compare == 0:
        # No close trade, encouter buy singal
        exit_loss = 0
        buy_price = df_val["close"].iloc[i]
        
        compare = 1
        logs.append(1)

    #Once we close a trade, we have to check in df_fine whether to exit or not

    elif (df_val["flag"].iloc[i] != -1 and compare == 1):
        # Current buy trade, encounter buy signal or no signal - do nothing, update stop loss
        logs.append(0)

        #calculate pnl, if we exit now
        sell_price = df_val["close"].iloc[i]
        exit_loss = (sell_price - buy_price)/buy_price 
        

        #exit trade, if the loss is higher than stop loss
        if exit_loss < thresh and disable_trading == 0:
            logs[-1] = -1
            # print(f"disable_trading in buy trade - stop loss: {disable_trading}")
            disable_trading = 1


    elif df_val["flag"].iloc[i] == -1 and compare == 1:
        # Current buy trade, encounter sell signal

        #exit trade
        logs.append(-1)
        compare = 0
        exit_loss = 0

        #if trade was already exited before, check for disable trading flag here, do nothing here
        if disable_trading == 1:
            disable_trading = 0
            # compare = -1
            # print(f"disable_trading in buy trade - while exiting: {disable_trading}")
            logs[-1] = 0


    #SHORT TRADES
    elif df_val["flag"].iloc[i] == -1 and compare == 0:
        # No close trade, enounter sell siganl 
        exit_loss = 0
        sell_price = df_val["close"].iloc[i]
        
        compare = -1
        logs.append(-1)


    elif (df_val["flag"].iloc[i] != 1 and compare == -1):
        # Current sell trade, encounter sell signal or no signal - do nothing, update stop loss
        logs.append(0)

        #calculate pnl, if we exit now
        buy_price = df_val["close"].iloc[i]
        exit_loss = (sell_price - buy_price)/sell_price 
    

        #exit trade, if the loss is higher than stop loss
        if exit_loss < thresh and disable_trading == 0:
            logs[-1] = 1
            # print(f"disable_trading in sell trade - stop loss: {disable_trading}")
            # print(i)
            disable_trading = 1

    elif df_val["flag"].iloc[i] == 1 and compare == -1:
        # 
        # print("Current sell trade, encounter buy signal")
        # print(f"{disable_trading}")

        #exit trade
        logs.append(1)
        compare = 0
        exit_loss = 0

        #if trade was already exited before, check for disable trading flag here, do nothing here
        if disable_trading == 1:
            # print("Check")
            disable_trading = 0
            logs[-1] = 0
            # compare = 1

    elif df_val["flag"].iloc[i] == 0 and compare == 0:
        logs.append(0)

#close out positions (if needed)
logs[-1] = -np.sum(logs)

df_val["logs"] = np.array(logs)

# rename column logs to signal
df_val.rename(columns={'logs': 'signal'}, inplace=True)

df_val.to_csv("../src/logs/lin_reg_val_" + time_frame + ".csv")