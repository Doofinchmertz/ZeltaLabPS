from sklearn.preprocessing import StandardScaler
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import sys
from sklearn.linear_model import LinearRegression, Lasso

def read_file(filename):
    return pd.read_csv(filename, index_col=0, parse_dates=True, infer_datetime_format=True)

def get_data(timeframe, name):
    return read_file("data_with_indicators/btcusdt_" + timeframe + "_" + name + ".csv")

# Tick Size of Data
time_frame = sys.argv[1]

k = sys.argv[2]

df = get_data(time_frame, 'total')

chunks = np.array_split(df, 100)

# Randomly split chunks into 70% and 30%
np.random.shuffle(chunks)
train_chunks = chunks[:60]
val_chunks = chunks[60:]

# Concatenate the chunks back into dataframes
df_train = pd.concat(train_chunks)
df_val = pd.concat(val_chunks)
df_test = df

model = Lasso(alpha=0.002, max_iter=1000)


# Define the independent variables
X_train = df_train.drop(f'Next_{k}_Days_Return', axis=1)
X_train = X_train.drop('open', axis=1)
X_val = df_val.drop(f'Next_{k}_Days_Return', axis=1)
X_val = X_val.drop('open', axis=1)
X_test = df_test.drop(f'Next_{k}_Days_Return', axis=1)
X_test = X_test.drop('open', axis=1)


# Define the dependent variable
y_train = df_train[f'Next_{k}_Days_Return']
y_val = df_val[f'Next_{k}_Days_Return']
y_test = df_test[f'Next_{k}_Days_Return']
# print(X_train.shape, y_train.shape)
# print(X_val.shape, y_val.shape)

df_train['indicator'] = 0
df_val['indicator'] = 0
df_test['indicator'] = 0

# Fit the linear regression model on the training data

# X_train.head()

model.fit(X_train, y_train)
print("model_coef", model.coef_)

# Predict the dependent variable of the training data
y_pred = model.predict(X_train)
quantile_value = np.quantile(np.abs(y_pred), 0.999)
print("quantile value: ", quantile_value)
print(np.corrcoef(y_pred, y_train)[0,1])

y_pred = model.predict(X_val)
print(np.corrcoef(y_pred, y_val)[0,1])

y_pred = model.predict(X_test)
print(np.corrcoef(y_pred, y_test)[0,1])

quantile_value = 0
df_test['indicator'] = np.where(y_pred > quantile_value, 1, np.where(y_pred < -quantile_value, -1, 0))
data = df_test

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
data.to_csv("../src/logs/lin_reg_test_" + time_frame + ".csv")

