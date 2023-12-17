import pandas as pd
import threading
import os
import talib
from collections import deque

ts = "3m"
data = pd.read_csv(f"../data/btcusdt_{ts}_diamond.csv")

def run_script(pl_window, pc_multiplier, sl_multiplier):
    try:
        df = data.copy()
        MEDIAN_WINDOW = 40
        REVERSION_THRESH = 2
        TREND_THRESH = 3
        STOPLOSS = 0.09
        PROFIT_CAP = 0.02
        MAX_TRADE_HOLD = 1800

        DI_WINDOW = 15
        DDI_REV_THRESH = 10
        DDI_TREND_THRESH = 50

        MIN_PROFIT_CAP = 0.004
        PROFIT_CAP_MULTIPLIER = pc_multiplier
        STOPLOSS_MULTIPLIER = sl_multiplier
        PROFIT_LOSS_WINDOW = pl_window

        q = deque(maxlen=PROFIT_LOSS_WINDOW)

        df['median'] = df['close'].rolling(MEDIAN_WINDOW).median().shift(1)
        df['std'] = df['close'].rolling(MEDIAN_WINDOW).std().shift(1)
        df['PLUS_DI'] = talib.PLUS_DI(df.high, df.low, df.close, timeperiod=DI_WINDOW)
        df['MINUS_DI'] = talib.MINUS_DI(df.high, df.low, df.close, timeperiod=DI_WINDOW)
        df['DDI'] = df['PLUS_DI'] - df['MINUS_DI']

        df['indicator'] = 0
        df['signal'] = 0

        df.dropna(inplace=True)

        tot = 0
        
        current_position = 0
        entry_idx = None

        for i in range(MEDIAN_WINDOW, len(df)):
            if current_position == 0:
                median = df['median'][i]
                std = df['std'][i]  
                if df['DDI'][i] < DDI_REV_THRESH and df['DDI'][i] > -DDI_REV_THRESH:
                    if df['close'][i] < median - std*REVERSION_THRESH:
                        df.at[i, 'indicator'] = 1
                    elif df['close'][i] > median + std*REVERSION_THRESH:
                        df.at[i, 'indicator'] = -1
                    else:
                        df.at[i, 'indicator'] = 0
                elif df['DDI'][i] > DDI_TREND_THRESH and df['volume'][i] > df['volume'][i-1] and df['close'][i] > median + std*TREND_THRESH:
                    df.at[i, 'indicator'] = 1
                elif df['DDI'][i] < -DDI_TREND_THRESH and df['volume'][i] > df['volume'][i-1] and df['close'][i] < median - std*TREND_THRESH:
                    df.at[i, 'indicator'] = -1
            else:
                PROFIT_CAP = max(PROFIT_CAP_MULTIPLIER*q.count('P')/len(q), MIN_PROFIT_CAP) if len(q) >= PROFIT_LOSS_WINDOW else PROFIT_CAP
                STOPLOSS = STOPLOSS_MULTIPLIER*(len(q) - q.count('S'))/len(q) if len(q) >= PROFIT_LOSS_WINDOW else STOPLOSS

                PROFIT_CAP = PROFIT_CAP * (1 - (i - entry_idx)/MAX_TRADE_HOLD)
                STOPLOSS = STOPLOSS * (1 - (i - entry_idx)/MAX_TRADE_HOLD)

                PROFIT_CAP = max(PROFIT_CAP, MIN_PROFIT_CAP)
                if i >= entry_idx + MAX_TRADE_HOLD:
                    df.at[i, 'indicator'] = -1*current_position
                    q.append('M')
                if current_position == 1:
                    if df['close'][i] > df['close'][entry_idx]*(1+PROFIT_CAP):
                        df.at[i, 'indicator'] = -1
                        q.append('P')
                    elif df['close'][i] < df['close'][entry_idx]*(1-STOPLOSS):
                        df.at[i, 'indicator'] = -1
                        q.append('S')
                elif current_position == -1:
                    if df['close'][i] < df['close'][entry_idx]*(1-PROFIT_CAP):
                        df.at[i, 'indicator'] = 1
                        q.append('P')
                    elif df['close'][i] > df['close'][entry_idx]*(1+STOPLOSS):
                        df.at[i, 'indicator'] = 1
                        q.append('S')
            starting_position = current_position
            if df['indicator'][i] == 1:
                if tot == 0 or tot == -1:
                    # enter long position/exit short position
                    tot += 1
                    df.at[i, 'signal'] = 1
                    current_position += 1
            elif df['indicator'][i] == -1:
                if tot == 0 or tot == 1:
                    # enter short position/exit long position
                    tot -= 1
                    df.at[i, 'signal'] = -1
                    current_position -= 1
            if starting_position == 0 and current_position != 0:
                entry_idx = i
            elif starting_position != 0 and current_position == 0:
                entry_idx = None
        df.to_csv(f"logs/{pl_window}_{int(pc_multiplier*1000)}_{int(sl_multiplier*1000)}.csv", index=False)
        os.system(f"python3 main_static.py --ts {ts} --logs logs/{pl_window}_{int(pc_multiplier*1000)}_{int(sl_multiplier*1000)}.csv > output/output_{pl_window}_{int(pc_multiplier*1000)}_{int(sl_multiplier*1000)}.txt")
        with open(f"output/output_{pl_window}_{int(pc_multiplier*1000)}_{int(sl_multiplier*1000)}.txt", "r") as file:
            pnl = float(file.readline().strip())
        print("PnL:", pnl, "pl_window:", pl_window, "pc_multiplier:", pc_multiplier, "sl_multiplier:", sl_multiplier)
        os.system(f"rm logs/{pl_window}_{int(pc_multiplier*1000)}_{int(sl_multiplier*1000)}.csv")
        os.system(f"rm output/output_{pl_window}_{int(pc_multiplier*1000)}_{int(sl_multiplier*1000)}.txt")
    finally:
        semaphore.release()


# best_pnl = -100000
# best_reversion_thresh = 0
# best_trend_thresh = 0

# lock = threading.Lock()
max_threads = 4
threads = []
semaphore = threading.BoundedSemaphore(max_threads)

for pl_window in [25]:
    for pc_multiplier in [0.05]:
        for sl_multiplier in [0.11]:
            semaphore.acquire()
            thread = threading.Thread(target = run_script, args = (pl_window, pc_multiplier, sl_multiplier))
            thread.start()
            threads.append(thread)

for thread in threads:
    thread.join()