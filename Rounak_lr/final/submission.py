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
k = int(2)
wsl = False
thresh = 0.2


# Tick Size of Data
time_frame = "1h"
# Load data
df_train = get_data(time_frame, "train")
df_val = get_data(time_frame, "val")


# Read the linear regression model
model = pickle.load(open("model.pkl", 'rb'))


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


df_train['flag'] = 0
df_val['flag'] = 0
# Fit the linear regression model on the training data

# Predict the dependent variable of the training data
y_pred = model.predict(X_train)
positive_quantile = float(92.45)/100
positive_quantile_value = np.quantile(np.abs(y_pred), positive_quantile)
negative_quantile = float(92.45)/100
negative_quantile_value = -np.quantile(np.abs(y_pred), negative_quantile)


data = None

df_train['flag'] = np.where(y_pred > positive_quantile_value, 1, np.where(y_pred < negative_quantile_value, -1, 0))
# Creating Logs for training data
if wsl:
    data = df_train
    tot = 0
    for index, _ in data.iterrows():
        data.at[index, 'signal'] = 0
        if data.at[index, 'flag'] == 1:
            if tot == 0 or tot == -1:
                # enter long position/exit short position
                tot += 1
                data.at[index, 'signal'] = 1
        elif data.at[index, 'flag'] == -1:
            if tot == 0 or tot == 1:
                # enter short position/exit long position
                tot -= 1
                data.at[index, 'signal'] = -1

    # Make the last signal -np.sum(data['signal']) to exit the trade
    # print(data['signal'].tail())
    data.at[index, 'signal'] = -np.sum(data['signal']) if tot != 0 else data.at[index, 'signal']

else:
    data = stop_loss(df_train, thresh)
    # print(data['signal'].head())    


data.to_csv("submission.csv")