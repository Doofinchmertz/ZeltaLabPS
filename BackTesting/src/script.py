import os
import sys
import matplotlib.pyplot as plt

max_k = 10
time_frame = sys.argv[1]
final_pnl_lst = []

for k in range(1, max_k + 1):
    print(f"Running for k = {k}")
    os.system(f"python3 evaluate_k.py {time_frame} {k}")
    os.system(f"python3 main_static.py --ts {time_frame} --logs logs/check_k_{time_frame}.csv > output_{time_frame}.txt")
    with open(f"output_{time_frame}.txt", "r") as file:
        first_line = file.readline()
        final_pnl_lst.append(float(first_line.strip()))
    
plt.plot(range(1, max_k + 1), final_pnl_lst)
plt.xlabel("k")
plt.ylabel("final pnl")
plt.xticks(range(1, max_k + 1))
plt.title(f"final pnl vs k for {time_frame} timeframe")
plt.savefig(f"plots/final_pnl_vs_k_{time_frame}.png")
plt.show()
