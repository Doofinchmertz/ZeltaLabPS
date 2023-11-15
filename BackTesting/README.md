# InterIITBacktesting

Logs required with column names: datetime, Open, Close, High, Low, Volume, signal

# Running the code

In order to run the code, go inside the `src/` folder. Put your log file inside a `logs/` folder.\
To run and test your strategy, run `python3 main_compounding.py --logs logs/filename.csv > output.txt`\
`output.txt` now has details of every trade executed, with net metrics in the end.
