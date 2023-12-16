import warnings
from Utils import *
import subprocess
from multiprocessing import Pool
warnings.filterwarnings("ignore")


def trade_analysis(df):

    df_trades= df[df["signal"] != 0].reset_index(drop = True)
 
    returns = []

    signs = []

    for i in range(0, len(df_trades), 2):

        entry_price = df_trades["close"].iloc[i]
        exit_price = df_trades["close"].iloc[i+1]
    

        sign = df_trades["signal"].iloc[i]

        returns.append(((exit_price-entry_price)/entry_price*sign - 0.15/100)*1000)
        # holding_times.append((end_time-start_time).days)
        signs.append(sign)
        # volumes.append(df_trades["volume"].iloc[i])

    return returns


def run_task(a):
    qp,qn = a
    result = subprocess.run(["python", "fit_linear_model.py", "--k", "2", "--ts", "1h", "--thresh", str(22/100), "--qp", str(qp/100), "--qn", str(qn/100)], capture_output=True, text=True)
    output = result.stdout
    pnl = output.split()
    tr_pnl = float(pnl[0])
    val_pnl = float(pnl[1])
    print(tr_pnl+val_pnl, tr_pnl, val_pnl, qp/100, qn/100)
    return tr_pnl + val_pnl

# range_q = range(94, 97, 1)
range_qp = range(8500,9500,70)
range_qn = range(8500,9500,70)
# range_t = [1000]
# pnls = [[0 for i in range_q] for j in range_t]
pnl_values = []
for qp in range_qp:
    with Pool(5) as p:
        pnl_values.extend(p.map(run_task, [(qp,qn) for qn in range_qn]))
        # pnls[t - 5][q-94] = pnl

# Find the best parameters
print("MAX PNL: ", max(pnl_values))
