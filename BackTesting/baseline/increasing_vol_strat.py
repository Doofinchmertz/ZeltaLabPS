import pandas as pd
import talib

df = pd.read_csv('../data/btcusdt_3m_train.csv')
df = df[df['volume']!=0]
df['curr_vol/prev_vol'] = df['volume'] / df['volume'].shift(1)
df['smavol'] = talib.SMA(df['volume'], timeperiod=3)
df['curr_vol/smavol'] = df['volume'] / df['smavol'].shift(1)
df['curr_vol/smavol'] = df['curr_vol/smavol'].fillna(1)
print(df['curr_vol/smavol'].describe())
# exit()

df['curr_vol/prev_vol'].fillna(1, inplace=True)
df['indicator'] = 0

inTrade = False
last_idx = -1
th = 12
gap = 3
curr_state = 0
count = 0
for i in range(len(df)):
    if i == last_idx + gap and last_idx > 0:
        df['indicator'].iloc[i] = -curr_state
        inTrade = False
        last_idx = -1
        curr_state = 0
        count += 1
    if df['curr_vol/smavol'].iloc[i] >= th and not inTrade:
        if df['close'].iloc[i] > df['open'].iloc[i]:
            df['indicator'].iloc[i] = 1
            inTrade = True
            last_idx = i
            curr_state = 1
        else:
            df['indicator'].iloc[i] = -1
            inTrade = True
            last_idx = i
            curr_state = -1
    
print(count)
df['signal'] = df['indicator']
df.to_csv('../src/logs/increasing_vol_strat.csv', index=False)
