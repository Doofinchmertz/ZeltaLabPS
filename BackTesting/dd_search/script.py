import pandas as pd
import threading

max_threads = 16
semaphore = threading.BoundedSemaphore(max_threads)
