import matplotlib.pyplot as plt
import os
import sys
import threading

# win = Tk() # Some Tkinter stuff
# screen_width = win.winfo_screenwidth() # Gets the resolution (width) of your monitor
# screen_height= win.winfo_screenheight() # Gets the resolution (height) of your monitor

def run_script(upper_treshold_natr, upper_treshold_mfi, lower_treshold_natr, lower_treshold_mfi, period_natr, period_mfi, lock):
    try:
        # print(f"At look back {look_back}, pred_window {pred_window}")
        os.system(fr"python .\Ayush\mfi_natr.py {upper_treshold_natr} {upper_treshold_mfi} {lower_treshold_natr} {lower_treshold_mfi} {period_natr} {period_mfi}")
        os.system(fr"python .\main_static.py --logs .\logs\mfi_natr_{upper_treshold_mfi}_{lower_treshold_mfi}_{upper_treshold_natr}_{lower_treshold_natr}_{period_mfi}_{period_natr}.csv --ts 1h > .\output\mfi_natr_{upper_treshold_natr}_{upper_treshold_mfi}_{lower_treshold_natr}_{lower_treshold_mfi}_{period_natr}_{period_mfi}.txt")
        with open(f".\output\mfi_natr_{upper_treshold_natr}_{upper_treshold_mfi}_{lower_treshold_natr}_{lower_treshold_mfi}_{period_natr}_{period_mfi}.txt", "r") as file:
            pnl = float(file.readline().strip())
        with lock:
            global best_pnl
            if pnl > best_pnl:
                best_pnl = pnl
                best_upper_treshold_mfi = upper_treshold_mfi
                best_lower_treshold_mfi = lower_treshold_mfi
                best_upper_treshold_natr = upper_treshold_natr
                best_lower_treshold_natr = lower_treshold_natr
                best_period_mfi = period_mfi
                best_period_natr = period_natr
                print("Best pnl:", best_pnl, "at upper cmo",best_upper_treshold_natr, "and lower cmo", best_lower_treshold_natr, "and period cmo", best_period_natr, "at upper mfi", best_upper_treshold_mfi, "and lower mfi", best_lower_treshold_mfi, "and period cmo", period_natr, "and period mfi", best_period_mfi)
            elif pnl > 0.9 * best_pnl:
                print("Best pnl:", best_pnl, "at upper cmo",upper_treshold_natr, "and lower cmo", lower_treshold_natr, "and period cmo", period_natr, "at upper mfi", upper_treshold_mfi, "and lower mfi", lower_treshold_mfi, "and period cmo", period_natr, "and period mfi", period_mfi)
            # else:
            #     print(pnl)
        # os.system(f"rm .\logs\obv_{short_window}_{long_window}_{span_b_window}.csv")
        os.remove(f".\logs\mfi_natr_{upper_treshold_mfi}_{lower_treshold_mfi}_{upper_treshold_natr}_{lower_treshold_natr}_{period_mfi}_{period_natr}.csv")
        os.remove(f".\output\mfi_natr_{upper_treshold_natr}_{upper_treshold_mfi}_{lower_treshold_natr}_{lower_treshold_mfi}_{period_natr}_{period_mfi}.txt")
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

best_upper_treshold_mfi = 1
best_lower_treshold_mfi = 1
best_upper_treshold_natr = 1
best_lower_treshold_natr = 1
best_period_mfi = 1
best_period_natr = 1


lock = threading.Lock()
threads = []

max_threads = 6
semaphore = threading.BoundedSemaphore(max_threads)

for upper_treshold_natr in range(5, 20, 2):
    for upper_treshold_mfi in range(58, 72, 4):
        for lower_treshold_natr in range(2, 100, 10):
            for lower_treshold_mfi in range(65, 80, 3):
                for period_natr in range(15, 35, 2):
                    for period_mfi in range(15, 35, 2):
                       
                        semaphore.acquire()
                        thread = threading.Thread(target=run_script, args=(upper_treshold_natr/10, upper_treshold_mfi, lower_treshold_natr/100, lower_treshold_mfi, period_natr, period_mfi, lock))
                        thread.start()
                        threads.append(thread)
                    # exit()
            
for thread in threads:
    thread.join()

print("Best pnl:", best_pnl, "at upper cmo",best_upper_treshold_natr, "and lower cmo", best_lower_treshold_natr, "and period cmo", best_period_natr, "at upper mfi", best_upper_treshold_mfi, "and lower mfi", best_lower_treshold_mfi, "and period mfi", best_period_mfi)

