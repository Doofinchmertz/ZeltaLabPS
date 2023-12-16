import pandas as pd
import numpy as np
import talib
import warnings
import sys
warnings.filterwarnings('ignore')

df1 = pd.read_csv(r"C:\Users\ayush\Desktop\IITB\ZeltaLabPS\BackTesting\dataset\train\btcusdt_1h_train.csv")
df2 = pd.read_csv(r"C:\Users\ayush\Desktop\IITB\ZeltaLabPS\BackTesting\src\Ayush\data.csv")

df2 = df2[['date', 'open', 'high', 'low', 'close']]
df2 = df2.rename(columns={'date': 'timestamp'})

df = pd.concat([df1, df2], ignore_index=True)
df = df.reset_index(drop=True)

upper_treshold= int(sys.argv[1])
lower_treshold= int(sys.argv[2])
period = int(sys.argv[3])
exit_neg = int(sys.argv[4])
exit_pos = int(sys.argv[5])

# upper_treshold = 70
# lower_treshold = 10
# period = 1
# exit = 1

df['CMO'] = talib.CMO(df['close'], timeperiod=period)
# df['CMO'] = df['TSF'] - df['close']

df['flag'] = df['CMO'].apply(lambda x: 1 if x > upper_treshold else (-1 if x < lower_treshold else 0))

def generate_signals(df, flag_column, exit=exit):
    compare = 0
    counter = 0

    signals = pd.Series(0, index=df.index, name='signal')

    for i in range(len(df)):
        if df[flag_column].iloc[i] == 1 and compare == 0:
            # No open trade, encounter buy signal
            compare = 1
            signals.iloc[i] = 1

        elif df[flag_column].iloc[i] == -1 and compare == 0:
            # Current buy trade, encounter sell signal or no signal - update stop loss
            signals.iloc[i] = -1
            compare = -1

        elif compare == 1:
            if counter < exit_pos:
                if df[flag_column].iloc[i] == 0:
                    counter += 1
                else:
                    if df[flag_column].iloc[i] == compare:
                        counter = counter // 2
                    else:
                        counter = 0
                        compare = 0
                        signals.iloc[i] = df[flag_column].iloc[i]

            else:
                signals.iloc[i] = -1 * compare
                counter = 0
                compare = 0

        elif compare == -1:
            if counter < exit_neg:
                if df[flag_column].iloc[i] == 0:
                    counter += 1
                else:
                    if df[flag_column].iloc[i] == compare:
                        counter = counter // 2
                    else:
                        counter = 0
                        compare = 0
                        signals.iloc[i] = df[flag_column].iloc[i]

            else:
                signals.iloc[i] = -1 * compare
                counter = 0
                compare = 0

    df['signal'] = signals

    
generate_signals(df, 'flag', exit=exit)
df.to_csv(rf"C:\Users\ayush\Desktop\IITB\ZeltaLabPS\BackTesting\src\logs\cmo_{upper_treshold}_{lower_treshold}_{period}_{exit_pos}_{exit_neg}.csv")