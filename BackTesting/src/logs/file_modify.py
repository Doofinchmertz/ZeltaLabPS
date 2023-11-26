
# import pandas as pd

# # read in csv file as dataframe
# df = pd.read_csv('ema_crossover_3m.csv')

# # shift the signal column by one value
# df['signal'] = df['signal'].shift(1)

# # delete the last value

# # put 0 as the new first value
# df.loc[0, 'signal'] = 0

# # save the new dataframe as ema_crossover_1h.csv
# df.to_csv('ema_crossover_3m.csv', index=False)


