import pandas as pd
import threading
import os
import concurrent.futures

ts = "3m"
df = pd.read_csv(f"../data/btcusdt_{ts}_train.csv")

def run_script(median_window, thresh, lock):
    try:
        data = df.copy()
        for i in range(median_window, len(data)):
            median = data['close'][i-median_window:i].median()
            if data.loc[i, 'close'] < median*(1 - thresh/100):
                data.at[i, 'indicator'] = 1
            elif data.loc[i, 'close'] > median*(1 + thresh/100):
                data.at[i, 'indicator'] = -1
            else:
                data.at[i, 'indicator'] = 0


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

        data.to_csv(f"logs/median_reversion_{ts}_{median_window}_{thresh}.csv")
        os.system(f"python3 main_static.py --ts 1h --logs logs/median_reversion_{ts}_{median_window}_{thresh}.csv > output/output_{ts}_{median_window}_{thresh}.txt")
        with open(f"output/output_{ts}_{median_window}_{thresh}.txt", "r") as file:
            pnl = float(file.readline().strip())
        with lock:
            global best_pnl, best_median_window, best_thresh
            if pnl > best_pnl:
                best_pnl = pnl
                best_median_window = median_window
                best_thresh = thresh
                print("Best PnL:", pnl, "at median window", median_window, "and thresh", thresh, "ts", ts)
            elif pnl > 0.9*best_pnl:
                print("Good PnL:", pnl, "at median window", median_window, "and thresh", thresh, "ts", ts)
        os.system(f"rm logs/median_reversion_{ts}_{median_window}_{thresh}.csv")
        os.system(f"rm output/output_{ts}_{median_window}_{thresh}.txt")
    finally:
        semaphore.release()


best_pnl = -100000
best_median_window = 0
best_thresh = 0

lock = threading.Lock()
max_threads = 16
threads = []
semaphore = threading.BoundedSemaphore(max_threads)

for median_window in range(60, 120, 10):
    print(f"Median window: {median_window}")
    for thresh in range(0, 10):
        semaphore.acquire()
        thread = threading.Thread(target = run_script, args = (median_window, thresh, lock))
        thread.start()
        threads.append(thread)

for thread in threads:
    thread.join()

print("Best PnL:", best_pnl, "at median window", best_median_window, "and thresh", best_thresh, "ts", ts)