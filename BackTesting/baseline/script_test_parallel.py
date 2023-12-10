from multiprocessing import Pool
import os
import matplotlib.pyplot as plt

output_file = "junk.txt"
max_k = 300
k = 1
time_frame = "1h"

# Define a function to run the task in a thread
def run_task(window):
    os.system(f"echo Hello {window}")
    os.system(f"python3 find_rsi_optimal.py {window} {k} {time_frame}")
    os.system(f"python3 main_static.py --logs logs/rsi_total_{window}_{k}_{time_frame}.csv --ts {time_frame} > output/output_{window}_{k}_{time_frame}.txt")
    pnl = 0
    with open(f"output/output_{window}_{k}_{time_frame}.txt") as file:
        first_line = file.readline()
        pnl = float(first_line.strip())
    print("HELOOOOOOOO", pnl)
    return pnl

# Create a list to hold the threads
pnl_values = []

if __name__ == '__main__':
    with Pool(5) as p:
        pnl_values = p.map(run_task, range(2, max_k + 1, 4))



    # Plot pnl_values
    plt.plot(range(2, max_k + 1, 4), pnl_values)
    plt.xlabel('Window')
    plt.ylabel('PnL')
    plt.title('PnL Values')
    plt.show()
