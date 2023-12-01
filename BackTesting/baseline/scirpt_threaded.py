import threading
import os

v1_values = {}
v2_values = {}
output_file = "junk.txt"
max_k = 100

# Define a function to run the task in a thread
def run_task(k):
    os.system(f"echo Hello {k}")
    os.system(f"python3 add_indicators.py train {k}")
    os.system(f"python3 add_indicators.py val {k}")
    os.system("python3 normalize_features.py")
    os.system(f"python3 fit_linear_model.py {k} > junk.txt")
    v1 = float(open(output_file).readlines()[0])
    v2 = float(open(output_file).readlines()[1])
    v1_values[k] = v1
    v2_values[k] = v2
    os.system("echo Hello done")

# Create a list to hold the threads
threads = []

# Iterate over the range of k values and create a thread for each task
for k in range(1, max_k + 1, 4):
    thread = threading.Thread(target=run_task, args=(k,))
    thread.start()
    threads.append(thread)

# Wait for all threads to finish
for thread in threads:
    thread.join()