import numpy as np
import pandas as pd

def money_flow_index(data, period=14):
    # Calculate typical price
    typical_price = (data['high'] + data['low'] + data['close']) / 3

    # Calculate raw money flow
    raw_money_flow = typical_price * data['volume']

    # Get the direction of the money flow
    money_flow_direction = [1 if typical_price[i] > typical_price[i - 1] else (-1 if typical_price[i] < typical_price[i - 1] else 0) for i in range(1, len(typical_price))]

    # Pad the money flow direction with 0 for the first element
    money_flow_direction.insert(0, 0)

    # Calculate positive and negative money flow
    positive_money_flow = [0 if direction == -1 else raw_money_flow[i] for i, direction in enumerate(money_flow_direction)]
    negative_money_flow = [0 if direction == 1 else raw_money_flow[i] for i, direction in enumerate(money_flow_direction)]

    # Calculate 14-day sums of positive and negative money flow
    positive_money_flow_sum = pd.Series(positive_money_flow).rolling(window=period, min_periods=1).sum()
    negative_money_flow_sum = pd.Series(negative_money_flow).rolling(window=period, min_periods=1).sum()

    # Calculate money flow index
    money_flow_ratio = positive_money_flow_sum / negative_money_flow_sum
    money_flow_index = 100 - (100 / (1 + money_flow_ratio))

    return money_flow_index

def pnl(df):

    df_trades= df[df["signal"] != 0].reset_index(drop = True)
    # print(len(df_trades))
 
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

    return np.sum(returns)

def stop_loss(data, thresh):

    exit_loss = 0
    disable_trading = 0
    compare = 0
    thresh = -thresh
    logs = []
    for i in range(len(data)):
        if data["flag"].iloc[i] == 1 and compare == 0:
            # No open trade, encouter buy singal
            exit_loss = 0
            buy_price = data["close"].iloc[i]
            
            compare = 1
            logs.append(1)

        #Once we close a trade, we have to check in df_fine whether to exit or not

        elif (data["flag"].iloc[i] != -1 and compare == 1):
            # Current buy trade, encounter buy signal or no signal - do nothing, update stop loss
            logs.append(0)

            #calculate pnl, if we exit now
            sell_price = data["close"].iloc[i]
            exit_loss = (sell_price - buy_price)/buy_price 
            

            #exit trade, if the loss is higher than stop loss
            if exit_loss < thresh and disable_trading == 0:
                logs[-1] = -1
                # print(f"disable_trading in buy trade - stop loss: {disable_trading}")
                disable_trading = 1


        elif data["flag"].iloc[i] == -1 and compare == 1:
            # Current buy trade, encounter sell signal

            #exit trade
            logs.append(-1)
            compare = 0
            exit_loss = 0

            #if trade was already exited before, check for disable trading flag here, do nothing here
            if disable_trading == 1:
                disable_trading = 0
                # compare = -1
                # print(f"disable_trading in buy trade - while exiting: {disable_trading}")
                logs[-1] = 0


        #SHORT TRADES
        elif data["flag"].iloc[i] == -1 and compare == 0:
            # No open trade, enounter sell siganl 
            exit_loss = 0
            sell_price = data["close"].iloc[i]
            
            compare = -1
            logs.append(-1)


        elif (data["flag"].iloc[i] != 1 and compare == -1):
            # Current sell trade, encounter sell signal or no signal - do nothing, update stop loss
            logs.append(0)

            #calculate pnl, if we exit now
            buy_price = data["close"].iloc[i]
            exit_loss = (sell_price - buy_price)/sell_price 
        

            #exit trade, if the loss is higher than stop loss
            if exit_loss < thresh and disable_trading == 0:
                logs[-1] = 1
                # print(f"disable_trading in sell trade - stop loss: {disable_trading}")
                # print(i)
                disable_trading = 1

        elif data["flag"].iloc[i] == 1 and compare == -1:
            # 
            # print("Current sell trade, encounter buy signal")
            # print(f"{disable_trading}")

            #exit trade
            logs.append(1)
            compare = 0
            exit_loss = 0

            #if trade was already exited before, check for disable trading flag here, do nothing here
            if disable_trading == 1:
                # print("Check")
                disable_trading = 0
                logs[-1] = 0
                # compare = 1

        elif data["flag"].iloc[i] == 0 and compare == 0:
            logs.append(0)

    #close out positions (if needed)
    logs[-1] = -np.sum(logs[:-1])

    data["logs"] = np.array(logs)

    # rename column logs to signal
    data.rename(columns={'logs': 'signal'}, inplace=True)

    return data



def read_file(filename):
    return pd.read_csv(filename, index_col=0, parse_dates=True, infer_datetime_format=True)


def get_data(timeframe, name):
    return read_file("data_with_new_indicators/btcusdt_" + timeframe + "_" + name + ".csv")


def ayush1(df):
    # Step 1: Calculate 7-day average of 'close'
    df['avg_close_7'] = df['close'].rolling(window=7).sum() / 7

    # Step 2: Subtract 'close' from the 7-day average
    df['avg_close_diff'] = df['avg_close_7'] - df['close']

    # Step 3: Scale the result
    df['scaled_avg_close_diff'] = (df['avg_close_diff'] - df['avg_close_diff'].mean()) / df['avg_close_diff'].std()

    # Step 4: Calculate 5-day delayed 'close'
    df['delayed_close_5'] = df['close'].shift(5)

    # Step 5: Calculate 230-day rolling correlation between 'vwap' and delayed 'close'
    df['corr_vwap_delayed_close'] = df['VWAP'].rolling(window=230).corr(df['delayed_close_5'])

    # Step 6: Scale the correlation and multiply by 20
    df['scaled_corr'] = (df['corr_vwap_delayed_close'] - df['corr_vwap_delayed_close'].mean()) / df['corr_vwap_delayed_close'].std()
    df['scaled_corr_20'] = 20 * df['scaled_corr']

    # Step 7: Combine the results
    df['result'] = df['scaled_avg_close_diff'] + df['scaled_corr_20']
