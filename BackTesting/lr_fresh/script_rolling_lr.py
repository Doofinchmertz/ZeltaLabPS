import pandas as pd
from sklearn.linear_model import LinearRegression, Ridge
import numpy as np
import threading
import os
import concurrent.futures

df = pd.read_csv("data/btcusdt_1h_train.csv")
df['datetime'] = pd.to_datetime(df['datetime'])
df.set_index(df['datetime'], inplace=True)

y = df['Next_2_Days_Return']
X = df.drop(['Next_2_Days_Return', 'open', 'close', 'datetime'], axis=1)

cut = 1.6

def run_script(look_back, pred_window, lock):
    try:
        data = df.copy()
        data['predicted_return'] = 0
        model = LinearRegression()
        for i in range(look_back, len(X) - pred_window, pred_window):
            model.fit(X[i-look_back:i], y[i-look_back:i])
            data.loc[data[i:i+pred_window].index, 'predicted_return'] = model.predict(X[i:i+pred_window])
        data.drop(data.index[:look_back], inplace=True)
        data['indicator'] = np.where(data['predicted_return'] > cut, 1, np.where(data['predicted_return'] < -cut, -1, 0))
        data['signal'] = 0
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
        data.to_csv(f"logs/rolling_lr_{look_back}_{pred_window}.csv")
        os.system(f"python3 main_static.py --ts 1h --logs logs/rolling_lr_{look_back}_{pred_window}.csv > output/output_rolling_lr_{look_back}_{pred_window}.txt")
        with open(f"output/output_rolling_lr_{look_back}_{pred_window}.txt", "r") as file:
            pnl = float(file.readline().strip())
        with lock:
            global best_pnl, best_look_back, best_pred_window
            if pnl > best_pnl:
                best_pnl = pnl
                best_look_back = look_back
                best_pred_window = pred_window
                print("Best PnL:", pnl, "at look back", look_back, "and pred window", pred_window)
            elif pnl > 0.9*best_pnl:
                print("Good PnL:", pnl, "at look back", look_back, "and pred window", pred_window)
        os.system(f"rm logs/rolling_lr_{look_back}_{pred_window}.csv")
        os.system(f"rm output/output_rolling_lr_{look_back}_{pred_window}.txt")
    finally:
        semaphore.release()

best_pnl = -100000
best_look_back = 0
best_pred_window = 0


lock = threading.Lock()
max_threads = 16
semaphore = threading.BoundedSemaphore(max_threads)
threads = []

lb_step = 96
pw_step = 24
with concurrent.futures.ThreadPoolExecutor(max_threads) as executor:
    for look_back in range(lb_step, lb_step*50, lb_step):
        print(f"Look back: {look_back}")
        for pred_window in range(pw_step, look_back, pw_step):
            semaphore.acquire()
            executor.submit(run_script, look_back, pred_window, lock)

print("Best PnL:", best_pnl, "at look back", best_look_back, "and pred window", best_pred_window)
