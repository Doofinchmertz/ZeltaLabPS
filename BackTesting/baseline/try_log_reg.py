import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import sys

def read_file(filename):
    return pd.read_csv(filename, index_col=0, parse_dates=True, infer_datetime_format=True)

def get_data(timeframe, name):
    return read_file("data_with_indicators/btcusdt_" + timeframe + "_" + name + ".csv")

time_frame = sys.argv[1]
df_train = get_data(time_frame, "train")
df_val = get_data(time_frame, "val")

df_train.drop('Next_1_Days_Return', axis=1, inplace=True)
df_val.drop('Next_1_Days_Return', axis=1, inplace=True)
X_train = df_train
X_val = df_val

y_train = np.where(df_train['close'].pct_change().shift(-1) > 0, 1, -1)
y_val = np.where(df_val['close'].pct_change().shift(-1) > 0, 1, -1)

y_train = y_train[:-1]
y_val = y_val[:-1]
X_train = X_train[:-1]
X_val = X_val[:-1]
df_train = df_train[:-1]
df_val = df_val[:-1]

clf = LogisticRegression(max_iter=1000)
clf.fit(X_train, y_train)

y_pred_train = clf.predict(X_train)
y_pred_val = clf.predict(X_val)

print(y_pred_train)
print(y_pred_val)

percentage_of_ones = np.mean(y_pred_val == 1) * 100
count_ones = np.count_nonzero(y_pred_val == 1)
count_neg_ones = np.count_nonzero(y_pred_val == -1)
print("Count of 1 in y_pred_val:", count_ones)
print("Count of -1 in y_pred_val:", count_neg_ones)
print("Percentage of values that are 1 in y_pred_val:", percentage_of_ones)


accuracy_train = accuracy_score(y_train, y_pred_train)
accuracy_val = accuracy_score(y_val, y_pred_val)

print("Training Accuracy:", accuracy_train)
print("Validation Accuracy:", accuracy_val)
print(clf.decision_function(X_val))

y_pred_train = np.where(clf.decision_function(X_train) > 0.7, 1, np.where(clf.decision_function(X_train) < -0.7, -1, 0))
y_pred_val = np.where(clf.decision_function(X_val) > 0.7, 1, np.where(clf.decision_function(X_val) < -0.7, -1, 0))

df_train['indicator'] = y_pred_train
df_val['indicator'] = y_pred_val

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
data.to_csv(f"../src/logs/try_log_reg_train.csv")

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
data.to_csv(f"../src/logs/try_log_reg_val.csv")
