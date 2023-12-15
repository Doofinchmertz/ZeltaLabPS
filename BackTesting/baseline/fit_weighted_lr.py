from sklearn.linear_model import LinearRegression
import pandas as pd
import sys
import numpy as np
import statsmodels.api as sm
from matplotlib import pyplot as plt

k = sys.argv[2]

def read_file(filename):
    return pd.read_csv(filename, index_col=0, parse_dates=True, infer_datetime_format=True)

def get_data(timeframe, name):
    return read_file("data_with_indicators/btcusdt_" + timeframe + "_" + name + ".csv")

# Tick Size of Data
time_frame = sys.argv[1]
# Load data
df_train = get_data(time_frame, "train")
df_val = get_data(time_frame, "val")

# Create the linear regression model


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
X_train = sm.add_constant(X_train)
mod_sm = sm.OLS(y_train, X_train)
res_sm = mod_sm.fit()
y_resid = [abs(resid) for resid in res_sm.resid]
X_resid = sm.add_constant(res_sm.fittedvalues)
mod_resid = sm.OLS(y_resid, X_resid)
res_resid = mod_resid.fit()
mod_fv = res_resid.fittedvalues
weights = 1 / (mod_fv**2)
X_train.drop('const', axis=1, inplace=True)
model = LinearRegression()
model.fit(X_train, y_train, sample_weight=weights)
y_pred = model.predict(X_train)

print(np.corrcoef(y_pred, y_train)[0,1])
quantile_value = 1.5

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
data.to_csv("../src/logs/lin_reg_train_" + time_frame + ".csv")

# Predict the dependent variable of the validation data
y_pred = model.predict(X_val)
print(np.corrcoef(y_pred, y_val)[0,1])

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
data.to_csv("../src/logs/lin_reg_val_" + time_frame + ".csv")