from sklearn.linear_model import LinearRegression
import numpy as np
import argparse
from Utils import *
import warnings
import pickle

warnings.filterwarnings("ignore")

parser = argparse.ArgumentParser()

# Add an argument k for the number of days to predict
parser.add_argument("--k", help="number of days to predict", required=True)

# boolean argument to indicate whether to use wsl or not
parser.add_argument("--wsl", help="use wsl or not", action='store_true')

# Timeframe of data
parser.add_argument("--ts", help="timeframe of data", default="1h")

# Threshold for stop loss
parser.add_argument("--thresh", help="threshold for stop loss", default=0.25)

# Quantile value for the trade
parser.add_argument("--qp", help="Quantile value for positive value", default=93)

# Quantile value for the trade
parser.add_argument("--qn", help="Quantile value for negative value", default=93)




# read the arguments and store it in a variable
args = parser.parse_args()
k = int(args.k)
wsl = args.wsl
thresh = float(args.thresh)


# Tick Size of Data
time_frame = args.ts
# Load data
df = get_data(time_frame, "complete")
total_length = len(df)

train_end = int(total_length * 0.60)
val_end = train_end + int(total_length * 0.20)

df_train = df[:train_end]
df_val = df[train_end:val_end]
df_test = df[val_end:]

# df_train = get_data(time_frame, "train")
# df_val = get_data(time_frame, "val")


# Define the independent variables
X_train = df_train.drop(f'Next_{k}_Days_Return', axis=1)
X_train = X_train.drop('open', axis=1)
X_train = X_train.drop('close', axis=1)
# X_train = X_train[['RSI', 'exp_RSI', 'MFI', 'EMA_Slope']]
print(X_train.columns)
X_val = df_val.drop(f'Next_{k}_Days_Return', axis=1)
X_val = X_val.drop('open', axis=1)
X_val = X_val.drop('close', axis=1)
# X_val = X_val[['RSI', 'exp_RSI', 'MFI', 'EMA_Slope']]
X_test= df_test.drop(f'Next_{k}_Days_Return', axis=1)
X_test = X_test.drop('open', axis=1)
X_test = X_test.drop('close', axis=1)

# Define the dependent variable
y_train = df_train[f'Next_{k}_Days_Return']
y_val = df_val[f'Next_{k}_Days_Return']
y_test = df_test[f'Next_{k}_Days_Return']

# Create the linear regression model using statsmodels
# model = sm.OLS(y_train, X_train).fit()
model = pickle.load(open("model.pkl", 'rb'))
model.fit(X_train[['volume', 'Daily_Return', 'RSI', 'exp_RSI', 'MFI', 'EMA_Slope']], y_train)

pickle.dump(model, open("model.pkl", 'wb'))


df_train['flag'] = 0
df_val['flag'] = 0
# Fit the linear regression model on the training data

print("model_coef", model.coef_)
# print(model.summary())

# Predict the dependent variable of the training data
y_pred = model.predict(X_train[['volume', 'Daily_Return', 'RSI', 'exp_RSI', 'MFI', 'EMA_Slope']])
positive_quantile = float(args.qp)/100
positive_quantile_value = np.quantile(np.abs(y_pred), positive_quantile)
negative_quantile = float(args.qn)/100
negative_quantile_value = -np.quantile(np.abs(y_pred), negative_quantile)
# print(f"quantile value at {quantile}: ", quantile_value)
# print("Training Correlation for the model is" ,np.corrcoef(y_pred, y_train)[0,1])
# quantile_value = 1.6



# Deciding Quantile value


data = None

df_train['flag'] = np.where(y_pred > positive_quantile_value, 1, np.where(y_pred < negative_quantile_value, -1, 0))
# Creating Logs for training data
if wsl:
    data = df_train
    tot = 0
    for index, _ in data.iterrows():
        data.at[index, 'signals'] = 0
        if data.at[index, 'flag'] == 1:
            if tot == 0 or tot == -1:
                # enter long position/exit short position
                tot += 1
                data.at[index, 'signals'] = 1
        elif data.at[index, 'flag'] == -1:
            if tot == 0 or tot == 1:
                # enter short position/exit long position
                tot -= 1
                data.at[index, 'signals'] = -1

    # Make the last signals -np.sum(data['signals']) to exit the trade
    # print(data['signals'].tail())
    data.at[index, 'signals'] = -np.sum(data['signals']) if tot != 0 else data.at[index, 'signals']

else:
    data = stop_loss(df_train, thresh)
    # print(data['signals'].head())    


data.to_csv("../src/logs/lin_reg_train_" + time_frame + ".csv")


# # print the pnl for training data
# print("PnL for training data is", pnl(data))
print(pnl(data))


# Prediction for validation data
y_pred = model.predict(X_val[['volume', 'Daily_Return', 'RSI', 'exp_RSI', 'MFI', 'EMA_Slope']])
# print("Validation Correlation for the model is", np.corrcoef(y_pred, y_val)[0,1])


df_val['flag'] = np.where(y_pred > positive_quantile_value, 1, np.where(y_pred < negative_quantile_value, -1, 0))
if wsl:
    data = df_val
    tot = 0
    for index, _ in data.iterrows():
        data.at[index, 'signals'] = 0
        if data.at[index, 'flag'] == 1:
            if tot == 0 or tot == -1:
                # enter long position/exit short position
                tot += 1
                data.at[index, 'signals'] = 1
        elif data.at[index, 'flag'] == -1:
            if tot == 0 or tot == 1:
                # enter short position/exit long position
                tot -= 1
                data.at[index, 'signals'] = -1

    data.at[index, 'signals'] = -np.sum(data['signals']) if tot != 0 else data.at[index, 'signals']

else:
    data = stop_loss(df_val, thresh)

data.to_csv("../src/logs/lin_reg_val_" + time_frame + ".csv")

# # print the pnl for validation data
# print("PnL for validation data is", pnl(data))
print(pnl(data))


# Prediction for test data
y_pred = model.predict(X_test[['volume', 'Daily_Return', 'RSI', 'exp_RSI', 'MFI', 'EMA_Slope']])
# print("Validation Correlation for the model is", np.corrcoef(y_pred, y_val)[0,1])


df_test['flag'] = np.where(y_pred > positive_quantile_value, 1, np.where(y_pred < negative_quantile_value, -1, 0))
if wsl:
    data = df_val
    tot = 0
    for index, _ in data.iterrows():
        data.at[index, 'signals'] = 0
        if data.at[index, 'flag'] == 1:
            if tot == 0 or tot == -1:
                # enter long position/exit short position
                tot += 1
                data.at[index, 'signals'] = 1
        elif data.at[index, 'flag'] == -1:
            if tot == 0 or tot == 1:
                # enter short position/exit long position
                tot -= 1
                data.at[index, 'signals'] = -1

    data.at[index, 'signals'] = -np.sum(data['signals']) if tot != 0 else data.at[index, 'signals']

else:
    data = stop_loss(df_val, thresh)

data.to_csv("../src/logs/lin_reg_test_" + time_frame + ".csv")

# # print the pnl for validation data
# print("PnL for validation data is", pnl(data))
print(pnl(data))