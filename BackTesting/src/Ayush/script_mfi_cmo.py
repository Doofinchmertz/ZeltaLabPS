import matplotlib.pyplot as plt
import os
import sys
import threading

# win = Tk() # Some Tkinter stuff
# screen_width = win.winfo_screenwidth() # Gets the resolution (width) of your monitor
# screen_height= win.winfo_screenheight() # Gets the resolution (height) of your monitor

def run_script(upper_treshold_cmo, upper_treshold_mfi, lower_treshold_cmo, lower_treshold_mfi, period_cmo, period_mfi, lock):
    try:
        # print(f"At look back {look_back}, pred_window {pred_window}")
        os.system(f"python .\Ayush\mfi_cmo.py {upper_treshold_cmo} {upper_treshold_mfi} {lower_treshold_cmo} {lower_treshold_mfi} {period_cmo} {period_mfi}")
        os.system(f"python .\main_static.py --logs .\logs\mfi_cmo_{upper_treshold_cmo}_{upper_treshold_mfi}_{lower_treshold_cmo}_{lower_treshold_mfi}_{period_cmo}_{period_mfi}.csv --ts 1h > .\output\mfi_cmo_{upper_treshold_cmo}_{upper_treshold_mfi}_{lower_treshold_cmo}_{lower_treshold_mfi}_{period_cmo}_{period_mfi}.txt")
        with open(f".\output\mfi_cmo_{upper_treshold_cmo}_{upper_treshold_mfi}_{lower_treshold_cmo}_{lower_treshold_mfi}_{period_cmo}_{period_mfi}.txt", "r") as file:
            pnl = float(file.readline().strip())
        with lock:
            global best_pnl
            if pnl > best_pnl:
                best_pnl = pnl
                best_upper_treshold_mfi = upper_treshold_mfi
                best_lower_treshold_mfi = lower_treshold_mfi
                best_upper_treshold_cmo = upper_treshold_cmo
                best_lower_treshold_cmo = lower_treshold_cmo
                best_period_mfi = period_mfi
                best_period_cmo = period_cmo
                print("Best pnl:", best_pnl, "at upper cmo",best_upper_treshold_cmo, "and lower cmo", best_lower_treshold_cmo, "and period cmo", best_period_cmo, "at upper mfi", best_upper_treshold_mfi, "and lower mfi", best_lower_treshold_mfi, "and period cmo", period_cmo, "and period mfi", best_period_mfi)
            elif pnl > 0.9 * best_pnl:
                print("Best pnl:", best_pnl, "at upper cmo",upper_treshold_cmo, "and lower cmo", lower_treshold_cmo, "and period cmo", period_cmo, "at upper mfi", upper_treshold_mfi, "and lower mfi", lower_treshold_mfi, "and period cmo", period_cmo, "and period mfi", period_mfi)
        # os.system(f"rm .\logs\obv_{short_window}_{long_window}_{span_b_window}.csv")
        os.remove(f".\logs\mfi_cmo_{upper_treshold_cmo}_{upper_treshold_mfi}_{lower_treshold_cmo}_{lower_treshold_mfi}_{period_cmo}_{period_mfi}.csv")
        os.remove(f".\output\mfi_cmo_{upper_treshold_cmo}_{upper_treshold_mfi}_{lower_treshold_cmo}_{lower_treshold_mfi}_{period_cmo}_{period_mfi}.txt")
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
best_upper_treshold_cmo = 1
best_lower_treshold_cmo = 1
best_period_mfi = 1
best_period_cmo = 1


lock = threading.Lock()
threads = []

max_threads = 6
semaphore = threading.BoundedSemaphore(max_threads)

for upper_treshold_cmo in range(22, 31, 4):
    for upper_treshold_mfi in range(58, 72, 4):
        for lower_treshold_cmo in range(120, 150, 5):
            for lower_treshold_mfi in range(65, 80, 3):
                for period_cmo in range(15, 35, 2):
                    for period_mfi in range(15, 35, 2):
                       
                        semaphore.acquire()
                        thread = threading.Thread(target=run_script, args=(upper_treshold_cmo, upper_treshold_mfi, lower_treshold_cmo, lower_treshold_mfi, period_cmo, period_mfi, lock))
                        thread.start()
                        threads.append(thread)
                    # exit()
            
for thread in threads:
    thread.join()

print("Best pnl:", best_pnl, "at upper cmo",best_upper_treshold_cmo, "and lower cmo", best_lower_treshold_cmo, "and period cmo", best_period_cmo, "at upper mfi", best_upper_treshold_mfi, "and lower mfi", best_lower_treshold_mfi, "and period mfi", best_period_mfi)

