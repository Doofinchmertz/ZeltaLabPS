from sklearn.linear_model import LinearRegression
import pandas as pd
import sys
import numpy as np

k = sys.argv[1]

def read_file(filename):
    return pd.read_csv(filename, index_col=0, parse_dates=True, infer_datetime_format=True)

def get_data(timeframe, name):
    return read_file("data_with_indicators/btcusdt_" + timeframe + "_" + name + ".csv")

# Tick Size of Data
time_frame = "5m"
# Load data
df_train = get_data(time_frame, "train")
df_val = get_data(time_frame, "val")

# df_train, df_val = train_test_split(df_, test_size=0.2, shuffle=False)

# Create the linear regression model
model = LinearRegression()


# Define the independent variables
X_train = df_train.drop(f'Next_{k}_Days_Return', axis=1)
X_train = X_train.drop('open', axis=1)
X_val = df_val.drop(f'Next_{k}_Days_Return', axis=1)
X_val = X_val.drop('open', axis=1)


# Define the dependent variable
y_train = df_train[f'Next_{k}_Days_Return']
y_val = df_val[f'Next_{k}_Days_Return']
# print(X_train.shape, y_train.shape)
# print(X_val.shape, y_val.shape)

df_train['indicator'] = 0
df_val['indicator'] = 0
# Fit the linear regression model on the training data

# X_train.head()

model.fit(X_train, y_train)

# Predict the dependent variable of the training data
y_pred = model.predict(X_train)

print(np.corrcoef(y_pred, y_train)[0,1])


df_train['indicator'] = 2*(y_pred > 0).astype(int) - 1
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

data['signal'] = data['signal'].shift(1)
data.at[data.index[0], 'signal'] = 0
data.to_csv("../src/logs/lin_reg_train_" + time_frame + ".csv")

# Predict the dependent variable of the validation data
y_pred = model.predict(X_val)
print(np.corrcoef(y_pred, y_val)[0,1])

df_val['indicator'] = 2*(y_pred > 0).astype(int) - 1
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
# data['signal'] = data['signal'].shift(1)
data.at[data.index[0], 'signal'] = 0
data.to_csv("../src/logs/lin_reg_val_" + time_frame + ".csv")