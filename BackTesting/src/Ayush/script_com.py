import matplotlib.pyplot as plt
import os
import sys
import threading

# win = Tk() # Some Tkinter stuff
# screen_width = win.winfo_screenwidth() # Gets the resolution (width) of your monitor
# screen_height= win.winfo_screenheight() # Gets the resolution (height) of your monitor

def run_script(short_window, long_window, span_b_window, upper_treshold, lower_treshold, lock):
    try:
        # print(f"At look back {look_back}, pred_window {pred_window}")
        os.system(f"python .\Ayush\mfi_ichi_com.py {short_window} {long_window} {span_b_window} {upper_treshold} {lower_treshold}")
        os.system(f"python .\main_static.py --logs .\logs\mfi_ichi_{short_window}_{long_window}_{span_b_window}_{upper_treshold}_{lower_treshold}.csv --ts 1h > .\output\output_{short_window}_{long_window}_{span_b_window}_{upper_treshold}_{lower_treshold}.txt")
        with open(f".\output\output_{short_window}_{long_window}_{span_b_window}_{upper_treshold}_{lower_treshold}.txt", "r") as file:
            pnl = float(file.readline().strip())
        with lock:
            global best_pnl
            if pnl > best_pnl:
                best_pnl = pnl
                best_short_window =  short_window
                best_long_window = long_window
                best_span_b_window = span_b_window
                best_upper_treshold = upper_treshold
                best_lower_treshold = lower_treshold
                print("Best pnl:", best_pnl, "at short",short_window, "and log window", long_window, "and span b window", span_b_window , "at upper",upper_treshold, "and lower", lower_treshold)
            elif pnl > 0.9 * best_pnl:
                print("Good pnl:", best_pnl, "at short",short_window, "and log window", long_window, "and span b window", span_b_window, "at upper",upper_treshold, "and lower", lower_treshold)
        # os.system(f"rm .\logs\obv_{short_window}_{long_window}_{span_b_window}.csv")
        os.remove(f".\logs\mfi_ichi_{short_window}_{long_window}_{span_b_window}_{upper_treshold}_{lower_treshold}.csv")
        os.remove(f".\output\output_{short_window}_{long_window}_{span_b_window}_{upper_treshold}_{lower_treshold}.txt")
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
best_short_window = 9
best_long_window = 26
best_span_b_window = 52
# best_displacement = 26
best_upper_treshold = 1
best_lower_treshold = 1


lock = threading.Lock()
threads = []

max_threads = 16
semaphore = threading.BoundedSemaphore(max_threads)

for short_window in range(22, 31, 4):
    for long_window in range(58, 72, 4):
        for span_b_window in range(120, 150, 5):
            for upper_treshold in range(65, 80, 3):
                for lower_treshold in range(15, 35, 2):
                    semaphore.acquire()
                    thread = threading.Thread(target=run_script, args=(short_window, long_window, span_b_window, upper_treshold, lower_treshold, lock))
                    thread.start()
                    threads.append(thread)
                # exit()
            
for thread in threads:
    thread.join()

print("Best pnl:", best_pnl, "at short",short_window, "and log window", long_window, "and span b window", span_b_window,  "at upper", upper_treshold, "and lower", lower_treshold)

