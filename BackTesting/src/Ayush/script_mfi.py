
import os
import sys
import threading
import subprocess

# win = Tk() # Some Tkinter stuff
# screen_width = win.winfo_screenwidth() # Gets the resolution (width) of your monitor
# screen_height= win.winfo_screenheight() # Gets the resolution (height) of your monitor

def run_script(upper_treshold, lower_treshold, period, exit, lock):
    try:
        # print(f"At look back {look_back}, pred_window {pred_window}")
        # upper_treshold = 23
        # lower_treshold = 12
        # period = 12
        # exit = 12

        # os.system(f"python .\Ayush\mfi_2.py {upper_treshold} {lower_treshold} {period} {exit}")
        # os.system(f"python .\main_static.py --logs  .\logs\mfi_{upper_treshold}_{lower_treshold}_{period}_{exit}.csv --ts 1h> .\output\output_{upper_treshold}_{lower_treshold}_{period}_{exit}.txt")
        # os.system(f"python .\main_compounding.py --logs .\logs\mfi_{upper_treshold}_{lower_treshold}_{period}_{exit}.csv > .\output\output_{upper_treshold}_{lower_treshold}_{period}_{exit}.txt")
 
        # Run the first command
        mfi_script_path = r".\Ayush\mfi_2.py"
        mfi_command = f"python {mfi_script_path} {upper_treshold} {lower_treshold} {period} {exit}"
        subprocess.run(mfi_command, shell=True)

        # Run the second command
        # main_script_path = r".\main_static.py"
        main_script_path = r".\main_compounding.py"

        logs_path = fr".\logs\mfi_{upper_treshold}_{lower_treshold}_{period}_{exit}.csv"
        output_path = fr".\output\output_{upper_treshold}_{lower_treshold}_{period}_{exit}.txt"
        # main_command = f"python {main_script_path} --logs {logs_path} --ts 1h > {output_path}"
        main_command = f"python {main_script_path} --logs {logs_path}  > {output_path}"

        subprocess.run(main_command, shell=True)

        # print("hi")
        with open(f".\output\output_{upper_treshold}_{lower_treshold}_{period}_{exit}.txt", "r") as file:
            pnl = float(file.readline().strip())
        with lock:
            global best_pnl
            if pnl > best_pnl:
                best_pnl = pnl
                best_upper_treshold = upper_treshold
                best_lower_treshold = lower_treshold
                best_period = period
                best_exit = exit    
                
                print("Best pnl:", best_pnl, "at upper",upper_treshold, "and lower", lower_treshold, "and period", period, "and exit", exit)
            elif pnl > 0.9 * best_pnl:
                print("Good pnl:", pnl, "at upper",upper_treshold, "and lower", lower_treshold, "and period", period, "and exit", exit)
        # os.system(f"rm .\logs\obv_{short_window}_{long_window}_{span_b_window}.csv")
        os.remove(f".\logs\mfi_{upper_treshold}_{lower_treshold}_{period}_{exit}.csv")
        os.remove(f".\output\output_{upper_treshold}_{lower_treshold}_{period}_{exit}.txt")
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
best_exit = 1

lock = threading.Lock()
threads = []

max_threads = 7
semaphore = threading.BoundedSemaphore(max_threads)

for upper_treshold in range(77, 85, 1):
    for lower_treshold in range(12, 16, 1):
        for period in range(8, 13, 1):
            for exit in range(12, 15, 1):
                semaphore.acquire()
                thread = threading.Thread(target=run_script, args=(upper_treshold, lower_treshold, period, exit, lock))
                thread.start()
                threads.append(thread)
        # exit()
            
for thread in threads:
    thread.join()

print("Best pnl:", best_pnl, "at upper",best_upper_treshold, "and lower", best_lower_treshold, "and period", best_period, "exit", best_exit)

