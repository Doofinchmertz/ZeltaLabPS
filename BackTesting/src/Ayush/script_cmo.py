import os
import sys
import threading

# win = Tk() # Some Tkinter stuff
# screen_width = win.winfo_screenwidth() # Gets the resolution (width) of your monitor
# screen_height= win.winfo_screenheight() # Gets the resolution (height) of your monitor

def run_script(upper_treshold, lower_treshold, period, exit_pos, exit_neg, lock):
    try:
        # print(f"At look back {look_back}, pred_window {pred_window}")
        os.system(f"python .\Ayush\CMO_hp.py {upper_treshold} {lower_treshold} {period} {exit_neg} {exit_pos}")
        os.system(f"python .\main_static.py --logs .\logs\cmo_{upper_treshold}_{lower_treshold}_{period}_{exit_pos}_{exit_neg}.csv --ts 1h > .\output\outcmo_{upper_treshold}_{lower_treshold}_{period}_{exit_pos}_{exit_neg}.txt")
        # print("hi")
        with open(f".\output\outcmo_{upper_treshold}_{lower_treshold}_{period}_{exit_pos}_{exit_neg}.txt", "r") as file:
            pnl = float(file.readline().strip())
        with lock:
            global best_pnl
            if pnl > best_pnl:
                best_pnl = pnl
                best_upper_treshold = upper_treshold
                best_lower_treshold = lower_treshold
                best_period = period
                best_exit_pos = exit_pos 
                best_exit_neg = exit_neg   
                
                print("Best pnl:", best_pnl, "at upper",upper_treshold, "and lower", lower_treshold, "and period", period, "and exit", exit_pos, "exit neg", exit_neg)
            elif pnl > 0.9 * best_pnl:
                print("Good pnl:", pnl, "at upper",upper_treshold, "and lower", lower_treshold, "and period", period, "and exit", exit_pos, "exit neg", exit_neg)
        # os.system(f"rm .\logs\obv_{short_window}_{long_window}_{span_b_window}.csv")
        os.remove(f".\logs\cmo_{upper_treshold}_{lower_treshold}_{period}_{exit_pos}_{exit_neg}.csv")
        os.remove(f".\output\outcmo_{upper_treshold}_{lower_treshold}_{period}_{exit_pos}_{exit_neg}.txt")
        # os.system(f"rm .\output\output_{short_window}_{long_window}_{span_b_window}.txt")
    finally:
        semaphore.release()

# if len(sys.argv) != 5:
#     print("Incorrect number of arguments passed.")
#     print("Usage: python3 script.py <time_frame> <k> <look_back_step> <pred_window_step>")
#     sys.exit(1)

# time_frame = sys.argv[1]
# k = int(sys.argv[2])

# os.system(f"python .\add_indicators.py {time_frame} {k}")

best_pnl = -100000
best_upper_treshold = 1
best_lower_treshold = 1
best_period = 1
best_exit_pos = 1
best_exit_neg = 1

lock = threading.Lock()
threads = []

max_threads = 7
semaphore = threading.BoundedSemaphore(max_threads)

for upper_treshold in range(15, 40, 2):
    for lower_treshold in range(40, 70, 2):
        for period in range(12, 21, 2):
            for exit_pos in range(10, 11, 5):
                for exit_neg in range(10, 32, 7):
                    semaphore.acquire()
                    thread = threading.Thread(target=run_script, args=(upper_treshold, -lower_treshold, period, exit_pos, exit_neg, lock))
                    thread.start()
                    threads.append(thread)
        # exit()
            
for thread in threads:
    thread.join()

print("Best pnl:", best_pnl, "at upper",best_upper_treshold, "and lower", best_lower_treshold, "and period", best_period, "exit", best_exit_pos, "exit neg", best_exit_neg)

