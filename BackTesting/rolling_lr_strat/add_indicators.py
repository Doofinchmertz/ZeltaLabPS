import pandas as pd
import talib
import numpy as np
from optimal_constants import *
import argparse

ts = "1h"  # tick size to trade
parser = argparse.ArgumentParser(description='Rolling LR Strategy')
parser.add_argument('--data', type=str, help='Path to the data file', required=True)
args = parser.parse_args()

df = pd.read_csv(args.data)

## Target Variable to Predict
df['Next_2h_Return'] = df['close'].shift(-2) / df['close'] - 1
df['Next_2h_Return'] = df['Next_2h_Return']*EACH_TRADE_VALUE

## Indicator 1 RSI
df['RSI'] = talib.RSI(df['close'], timeperiod=RSI_TIME_PERIOD)
df['RSI'] -= 50
df['RSI'] = df['RSI'].apply(lambda x: x if x > RSI_CUT or x < -RSI_CUT else 0)
df['RSI'] = df['RSI'].apply(lambda x: x - RSI_CUT if x >= RSI_CUT else x)
df['RSI'] = df['RSI'].apply(lambda x: x + RSI_CUT if x <= -RSI_CUT else x)                            
df.fillna(0,inplace=True)

## Indicator 2 exp_RSI
df['exp_RSI'] = 0
df['exp_RSI'] = np.exp(np.abs(df['RSI']))
df['exp_RSI'] = np.where(df['RSI'] > 0, -df['exp_RSI'], df['exp_RSI'])

## Indicator 3 EMA_Slope
df['EMA'] = talib.EMA(df['close'], timeperiod=EMA_TIME_PERIOD)
df['EMA_Slope'] = -df['EMA'].pct_change(1)*100

## Indicator 4 ADOSC
df['ADOSC'] = talib.ADOSC(df['high'], df['low'], df['close'], df['volume'], fastperiod=ADOSC_FAST_PERIOD, slowperiod=ADOSC_SLOW_PERIOD)

## Indicator 5 MACD Signal
macd, signal, _ = talib.MACD(df["close"], fastperiod=MACD_FAST_PERIOD, slowperiod=MACD_SLOW_PERIOD, signalperiod=MACD_SIGNAL_PERIOD)
df['macd'] = macd
df['signal'] = signal
shifted_signal = df['signal'].shift(1)
shifted_signal.fillna(0, inplace=True)
df['macd'].fillna(0, inplace=True)
df['macd_signal'] = df['signal'] - shifted_signal

## Saving the data with indicators
df = df.drop(['macd', 'signal', 'EMA'], axis=1)
df.dropna(inplace=True)
df.to_csv(f"data_with_indicators/btcusdt_{ts}.csv", index=False)
