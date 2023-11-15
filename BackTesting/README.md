# InterIITBacktesting

Logs required with column names: datetime, Open, Close, High, Low, Volume, signal

# Running the code

There are two ways of executing order:
1. static : each trade executed is worth 1000$
2. compounding : start with 1000$, execute next trade with the current cash.(One wierd thing in current implementation is say, you start with 1000, you give a selll order, then a buy order. The buy order will buy assets worth 2000)

In order to run the code, go inside the `src/` folder. Put your log file inside a `logs/` folder.\
To run and test your strategy, run `python3 main_static.py --logs logs/filename.csv > output.txt` to execute the orders static way\
Run `python3 main_compounding.py --logs logs/filename.csv > output.txt`\
`output.txt` now has details of every trade executed, with net metrics in the end\
Run the scripts with --gen_vis_logs flag to generate csv files with plotting data for each timestamp\
Currently static way generates csv with columns : 'Trade PnL', 'Net PnL'\
compounding way generates csv with columns : 'Net Returns', 'Net Value', 'Net Assets', 'Net Cash'\

