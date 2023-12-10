from sklearn.linear_model import LinearRegression, Ridge, Lasso
import pandas as pd
import sys
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

k = int(sys.argv[2])

def read_file(filename):
    return pd.read_csv(filename, index_col=0, parse_dates=True, infer_datetime_format=True)

def get_data(timeframe, name):
    return read_file("data/btc_" + timeframe + "_" + name + ".csv")

# Tick Size of Data
time_frame = sys.argv[1]
# Load data
df_train = get_data(time_frame, "train")
df_val = get_data(time_frame, "val")

# Create the linear regression model
model = LinearRegression()

# Define the dependent variable
y_train = df_train.filter(like = 'target')
y_val = df_val.filter(like = 'target')

# Define the independent variables
X_train = df_train.drop(y_train.columns, axis=1)
X_train = X_train.drop(['open', 'high', 'low', 'close'], axis=1)
scaler = StandardScaler()
X_normalized = scaler.fit_transform(X_train)
X_train = pd.DataFrame(X_normalized, columns=X_train.columns)
pca = PCA()
X_pca = pca.fit_transform(X_train)
X_train = X_pca[:,:5]

X_val = df_val.drop(y_val.columns, axis=1)
X_val = X_val.drop(['open', 'high', 'low', 'close'], axis=1)
X_normalized = scaler.transform(X_val)
X_val = pd.DataFrame(X_normalized, columns=X_val.columns)
X_pca = pca.transform(X_val)
X_val = X_pca[:,:5]

y_train = y_train[f'target_{k}d']
y_val = y_val[f'target_{k}d']


df_train['indicator'] = 0
df_val['indicator'] = 0
# Fit the linear regression model on the training data

# X_train.head()

model.fit(X_train, y_train)

# Predict the dependent variable of the training data
y_pred = model.predict(X_train)
# quantile_value = np.quantile(np.abs(y_pred), 0.99)
# print("quantile value: ", quantile_value)
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

# Predict the dependent variable of the validationdata
y_pred = model.predict(X_val)
print(np.corrcoef(y_pred, y_val)[0,1])
print(pd.Series(y_pred).describe())
print(pd.Series(y_val).describe())

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