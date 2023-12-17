import os
import sys
import threading

# win = Tk() # Some Tkinter stuff
# screen_width = win.winfo_screenwidth() # Gets the resolution (width) of your monitor
# screen_height= win.winfo_screenheight() # Gets the resolution (height) of your monitor

def run_script(length, mult, lock):
    try:
        # print(f"At look back {look_back}, pred_window {pred_window}")
        os.system(f"python .\Ayush\ollinger.py {length} {mult}")
        os.system(f"python .\main_static.py --logs .\logs\ollin_{length}_{mult}.csv --ts 1h > .\output\outbollin_{length}_{mult}.txt")
        # print("hi")
        with open(f".\output\outbollin_{length}_{mult}.txt", "r") as file:
            pnl = float(file.readline().strip())
        with lock:
            global best_pnl
            if pnl > best_pnl:
                best_pnl = pnl
                best_length = length
                best_mult = mult
              
                print("Best pnl:", best_pnl, "at length",length, "and mult", mult)
            elif pnl > 0.9 * best_pnl:
                print("Good pnl:", pnl, "at length",length, "and mult", mult)
        # os.system(f"rm .\logs\obv_{short_window}_{long_window}_{span_b_window}.csv")
        os.remove(f".\logs\ollin_{length}_{mult}.csv")
        os.remove(f".\output\outbollin_{length}_{mult}.txt")
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
best_length = 1
best_mult = 1

lock = threading.Lock()
threads = []

max_threads = 7
semaphore = threading.BoundedSemaphore(max_threads)

for length in range(65, 81, 1):
    for mult in range(25, 35, 1):
            semaphore.acquire()
            thread = threading.Thread(target=run_script, args=(length, mult/10, lock))
            thread.start()
            threads.append(thread)
        # exit()
            
for thread in threads:
    thread.join()

print("Best pnl:", best_pnl, "at length",length, "and mult", mult)

