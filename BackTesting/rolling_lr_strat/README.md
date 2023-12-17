# Rolling_LR

This folder contains the implementation of the `rolling_lr`, a trading strategy based on continuously updated linear regression 

## Files

- **add_indicator.py**: This script adds technical indicators to the given data file. It takes one argument, `data`, which is the name of the file. The data file should be located in the `data` folder in the main directory.

```
python3 add_indicators.py --data data_file.csv
```
- **rolling_lr.py**: This script runs a rolling linear regression model to the data file as saved by add_indicator.py

```
python3 rolling_lr.py
```
- **Optimal_constants.py**: This file contains optimal constants used throughout the directory. These constants have been set after rigorous testing to get the best performance metrics possible.

## Usage

To use this strategy, follow these steps:

1. Make sure you setup your environment using the `requirements.txt` file in this directory
2. Place the data file in the `data` folder in the main directory. (ex - data_file.csv)
3. Run the `add_indicators.py` script, passing the name of the data file as the argument. (An example command has been shown above)
4. Run the `rolling_lr.py`
   
## Logs
Logs for this strategy can be found in the `logs` folder of this directory