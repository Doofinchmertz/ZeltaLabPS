import matplotlib.pyplot as plt
import os
import sys
import threading
import pywhatkit
import pyautogui
from tkinter import *
import time

# win = Tk() # Some Tkinter stuff
# screen_width = win.winfo_screenwidth() # Gets the resolution (width) of your monitor
# screen_height= win.winfo_screenheight() # Gets the resolution (height) of your monitor

def run_script(look_back, pred_window, lock):
    try:
        print(f"At look back {look_back}, pred_window {pred_window}")
        os.system(f"python3 window_moving_lr_prices.py {time_frame} {k} {look_back} {pred_window}")
        os.system(f"python3 main_static.py --logs logs/window_moving_lr_prices_{time_frame}_{k}_{look_back}_{pred_window}.csv --ts {time_frame} > output/output_{time_frame}_{k}_{look_back}_{pred_window}.txt")
        with open(f"output/output_{time_frame}_{k}_{look_back}_{pred_window}.txt", "r") as file:
            pnl = float(file.readline().strip())
        with lock:
            global best_pnl, best_look_back, best_pred_window
            if pnl > best_pnl:
                best_pnl = pnl
                best_look_back = look_back
                best_pred_window = pred_window
                print("New best pnl:", best_pnl, "at look back", best_look_back, "and pred window", best_pred_window)
                # pywhatkit.sendwhatmsg_instantly("+919461244623", f"New best pnl: {best_pnl}, at look back: {best_look_back}, and pred window: {best_pred_window}", 20) # Sends the message
                # pyautogui.moveTo(screen_width * 0.5, screen_height* 0.5) # Moves the cursor the the message bar in Whatsapp
                # time.sleep(5)
                # pyautogui.click() # Clicks the bar
                # pyautogui.press('enter')
        os.system(f"rm logs/window_moving_lr_prices_{time_frame}_{k}_{look_back}_{pred_window}.csv")
        os.system(f"rm output/output_{time_frame}_{k}_{look_back}_{pred_window}.txt")
    finally:
        semaphore.release()

if len(sys.argv) != 5:
    print("Incorrect number of arguments passed.")
    print("Usage: python3 script.py <time_frame> <k> <look_back_step> <pred_window_step>")
    sys.exit(1)

time_frame = sys.argv[1]
k = int(sys.argv[2])

os.system(f"python3 add_indicators.py {time_frame} {k}")

best_pnl = -100000
best_look_back = 0
best_pred_window = 0

lock = threading.Lock()
threads = []
lb_step = int(sys.argv[3])
pw_step = int(sys.argv[4])

max_threads = 16
semaphore = threading.BoundedSemaphore(max_threads)

for look_back in range(lb_step, 50*lb_step, lb_step):
    for pred_window in range(pw_step, look_back//2, pw_step):
        semaphore.acquire()
        thread = threading.Thread(target=run_script, args=(look_back, pred_window, lock))
        thread.start()
        threads.append(thread)

for thread in threads:
    thread.join()

print("Best pnl:", best_pnl, "at look back", best_look_back, "and pred window", best_pred_window)

