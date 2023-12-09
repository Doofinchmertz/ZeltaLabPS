import threading
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
import numpy as np
import math

df = pd.read_csv('data/btc_1h_train.csv')
df.drop(['open', 'high', 'low', 'close'], axis=1, inplace=True)
y = df.filter(like = 'target')
X = df.drop(y.columns, axis=1)
X = X.drop('datetime', axis=1)
scaler = StandardScaler()
X_normalized = scaler.fit_transform(X)
X = pd.DataFrame(X_normalized, columns=X.columns)
y = pd.DataFrame(y, columns=y.columns)
target_k = 4

def run_script(look_back, pred_window, alpha, lock):
    try:
        # print("Running with look back", look_back, "and pred window", pred_window, "and alpha", alpha)
        model = Ridge(alpha=alpha)
        y_pred = []
        y_actual = []
        for i in range(look_back, len(X) - pred_window, pred_window):
            model.fit(X[i-look_back:i-target_k], y[i-look_back:i-target_k][f'target_{target_k}d'])
            y_pred = y_pred + model.predict(X[i:i+pred_window]).tolist()
            y_actual = y_actual + y[i:i+pred_window][f'target_{target_k}d'].tolist()

        y_pred = np.array(y_pred)
        y_actual = np.array(y_actual)
        count_greater = ((y_actual > 1.5) & (y_pred > 1.5)).sum()
        count_less = ((y_actual < -1.5) & (y_pred < -1.5)).sum()
        total_samples = len(y_actual)

        percentage_greater = (count_greater / total_samples) * 100
        percentage_less = (count_less / total_samples) * 100

        count_pred_greater = (y_pred > 1.5).sum()
        count_pred_less = (y_pred < -1.5).sum()
        percentage_pred_greater = (count_pred_greater / total_samples) * 100
        percentage_pred_less = (count_pred_less / total_samples) * 100

        count_actual_greater = (y_actual > 1.5).sum()
        count_actual_less = (y_actual < -1.5).sum()
        percentage_actual_greater = (count_actual_greater / total_samples) * 100
        percentage_actual_less = (count_actual_less / total_samples) * 100

        metric = ((percentage_greater + percentage_less)*(percentage_greater + percentage_less))/((percentage_actual_greater + percentage_actual_less)*(percentage_pred_greater + percentage_pred_less))
        metric = math.sqrt(metric)
        with lock:
            global best_metric, best_look_back, best_pred_window, best_alpha
            if metric > best_metric:
                best_metric = metric
                best_look_back = look_back
                best_pred_window = pred_window
                best_alpha = alpha
                print("New best metric:", best_metric, "at look back", best_look_back, "and pred window", best_pred_window, "and alpha", best_alpha)
            elif metric > 0.9*best_metric:
                print("Good metric:", metric, "at look back", look_back, "and pred window", pred_window, "and alpha", alpha)
    finally:
        semaphore.release()

best_metric = 0
best_look_back = 0
best_pred_window = 0
best_alpha = 0.000000001

lock = threading.Lock()
threads = []
max_threads = 16
semaphore = threading.BoundedSemaphore(max_threads)

lb_step = 96
pred_step = 24
for look_back in range(lb_step, lb_step*50, lb_step):
    for pred_window in range(pred_step, look_back//2, pred_step):
        for alpha in [0.001, 0.01, 0.1, 1, 10, 100, 1000]:
            semaphore.acquire()
            thread = threading.Thread(target=run_script, args=(look_back, pred_window, alpha, lock))
            thread.start()
            threads.append(thread)

for thread in threads:
    thread.join()

print("Best metric:", best_metric, "at look back", best_look_back, "and pred window", best_pred_window, "and alpha", best_alpha)