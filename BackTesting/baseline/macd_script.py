import pandas as pd
import numpy as np
import talib
import threading
import os
import sys

dict = {
    '05:30:00' : 530,
    '06:30:00' : 630,
    '07:30:00' : 730,
    '08:30:00' : 830,
    '09:30:00' : 930,
    '10:30:00' : 1030,
    '11:30:00' : 1130,
    '12:30:00' : 1230,
    '13:30:00' : 1330,
    '14:30:00' : 1430,
    '15:30:00' : 1530,
    '16:30:00' : 1630,
    '17:30:00' : 1730,
    '18:30:00' : 1830,
    '19:30:00' : 1930,
    '20:30:00' : 2030,
    '21:30:00' : 2130,
    '22:30:00' : 2230,
    '23:30:00' : 2330,
    '00:30:00' : 30,
    '01:30:00' : 130,
    '02:30:00' : 230,
    '03:30:00' : 330,
    '04:30:00' : 430,
}

def macd_strat(fast, slow, signal_win, datetime, sl_thresh):
    #read dataframe
    df = pd.read_csv("../data/btcusdt_1h_train.csv")
    df["datetime"] = pd.to_datetime(df["datetime"])

    df = df[df['datetime'].dt.time == pd.to_datetime(datetime).time()]
    macd, signal, _ = talib.MACD(df["open"], fastperiod=fast, slowperiod=slow, signalperiod=signal_win)
    df['macd'] = macd
    df['signal'] = signal
    shifted_signal = df['signal'].shift(1)
    df['flag'] = np.where(df['signal'] > shifted_signal, 1, 0)
    df['flag'] = np.where(df['signal'] < shifted_signal, -1, df['flag'])

    exit_loss = 0
    disable_trading = 0
    # stop_loss = 0
    compare = 0
    thresh = -0.01*sl_thresh
    logs = []
    for i in range(len(df)):
        if df["flag"].iloc[i] == 1 and compare == 0:
            # No open trade, encouter buy singal
            exit_loss = 0
            buy_price = df["open"].iloc[i]
            
            compare = 1
            logs.append(1)

        #Once we open a trade, we have to check in df_fine whether to exit or not

        elif (df["flag"].iloc[i] != -1 and compare == 1):
            # Current buy trade, encounter buy signal or no signal - do nothing, update stop loss
            logs.append(0)

            #calculate pnl, if we exit now
            sell_price = df["open"].iloc[i]
            exit_loss = (sell_price - buy_price)/buy_price 
            

            #exit trade, if the loss is higher than stop loss
            if exit_loss < thresh and disable_trading == 0:
                logs[-1] = -1
                # print(f"disable_trading in buy trade - stop loss: {disable_trading}")
                disable_trading = 1


        elif df["flag"].iloc[i] == -1 and compare == 1:
            # Current buy trade, encounter sell signal

            #exit trade
            logs.append(-1)
            compare = 0
            exit_loss = 0

            #if trade was already exited before, check for disable trading flag here, do nothing here
            if disable_trading == 1:
                disable_trading = 0
                # print(f"disable_trading in buy trade - while exiting: {disable_trading}")
                logs[-1] = 0


        #SHORT TRADES
        elif df["flag"].iloc[i] == -1 and compare == 0:
            # No open trade, enounter sell siganl 
            exit_loss = 0
            sell_price = df["open"].iloc[i]
            
            compare = -1
            logs.append(-1)


        elif (df["flag"].iloc[i] != 1 and compare == -1):
            # Current sell trade, encounter sell signal or no signal - do nothing, update stop loss
            logs.append(0)

            #calculate pnl, if we exit now
            buy_price = df["open"].iloc[i]
            exit_loss = (sell_price - buy_price)/sell_price 
        

            #exit trade, if the loss is higher than stop loss
            if exit_loss < thresh and disable_trading == 0:
                logs[-1] = 1
                # print(f"disable_trading in sell trade - stop loss: {disable_trading}")
                # print(i)
                disable_trading = 1

        elif df["flag"].iloc[i] == 1 and compare == -1:
            # 
            # print("Current sell trade, encounter buy signal")
            # print(f"{disable_trading}")

            #exit trade
            logs.append(1)
            compare = 0
            exit_loss = 0

            #if trade was already exited before, check for disable trading flag here, do nothing here
            if disable_trading == 1:
                # print("Check")
                disable_trading = 0
                logs[-1] = 0

        elif df["flag"].iloc[i] == 0 and compare == 0:
            logs.append(0)

    #close out positions (if needed)
    logs[-1] = -np.sum(logs)

    df["logs"] = np.array(logs)

    df_filter = df[['datetime', 'open', 'high', 'low', 'close', 'volume', 'logs']]
    df_filter.columns = ["datetime", 'open', 'high', 'low', 'close', 'volume', 'signal']
    df_filter = df_filter.reset_index(drop=True)
    df_filter.to_csv(f'logs/macd_signalthresh_{fast}_{slow}_{signal_win}_{dict[datetime]}_{sl_thresh}.csv', index=False)
    

def run(fast, slow, signal_win, datetime, sl_thresh):
    try:
        macd_strat(fast, slow, signal_win, datetime, sl_thresh)
        os.system(f"python3 main_static.py --logs logs/macd_signalthresh_{fast}_{slow}_{signal_win}_{dict[datetime]}_{sl_thresh}.csv --ts 1h > output/output_macd_signalthresh_{fast}_{slow}_{signal_win}_{dict[datetime]}_{sl_thresh}.txt")
        with open(f"output/output_macd_signalthresh_{fast}_{slow}_{signal_win}_{dict[datetime]}_{sl_thresh}.txt", "r") as file:
            pnl = float(file.readline().strip())
        with lock:
            global best_pnl, best_fast, best_slow, best_signal, best_sl_thresh, best_time
            if pnl > best_pnl:
                best_pnl = pnl
                best_fast = fast
                best_slow = slow
                best_signal = signal_win
                best_sl_thresh = sl_thresh
                best_time = datetime
                print("New best pnl:", best_pnl, "at fast", best_fast, "slow", best_slow, "signal", best_signal, "sl_thresh", best_sl_thresh, "time", best_time)
            else:
                if pnl > 0.9 * best_pnl:
                    print("Good pnl:", pnl, "at fast", fast, "slow", slow, "signal", signal_win, "sl_thresh", sl_thresh, "time", datetime)
        os.system(f"rm logs/macd_signalthresh_{fast}_{slow}_{signal_win}_{dict[datetime]}_{sl_thresh}.csv")
        os.system(f"rm output/output_macd_signalthresh_{fast}_{slow}_{signal_win}_{dict[datetime]}_{sl_thresh}.txt")
    finally:
        semaphore.release()


best_pnl = -100000
best_fast = 0
best_slow = 0
best_signal = 0
best_sl_thresh = 0
best_time = '05:30:00'
times = ['05:30:00', '06:30:00', '07:30:00', '08:30:00', '09:30:00',
       '10:30:00', '11:30:00', '12:30:00', '13:30:00', '14:30:00',
       '15:30:00', '16:30:00', '17:30:00', '18:30:00', '19:30:00',
       '20:30:00', '21:30:00', '22:30:00', '23:30:00', '00:30:00',
       '01:30:00', '02:30:00', '03:30:00', '04:30:00']
sl_list = range(1,11,1)


lock = threading.Lock()
threads = []
max_threads = 16
semaphore = threading.BoundedSemaphore(max_threads)

for fast in range(12, 50, 4):
    for slow in range(2*fast, min(3*fast, 50), 4):
        for signal_win in range(2, 2*fast, 4):
            for datetime in times:
                for sl in sl_list:
                    semaphore.acquire()
                    thread = threading.Thread(target=run, args=(fast, slow, signal_win, datetime, sl))
                    thread.start()
                    threads.append(thread)

for thread in threads:
    thread.join()

print("Best pnl:", best_pnl, "at fast", best_fast, "slow", best_slow, "signal", best_signal, "sl_thresh", best_sl_thresh, "time", best_time)