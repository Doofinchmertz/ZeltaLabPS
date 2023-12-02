import matplotlib.pyplot as plt
import os
import argparse
import pandas as pd

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--logs", help="path to logs file", nargs="+", required=True)
    args = parser.parse_args()

    df = pd.read_csv(args.logs[0])
    # Extract the required columns
    df = df[['datetime', 'open']]
    # Convert the datetime column to datetime type
    df['datetime'] = pd.to_datetime(df['datetime'])
    # Set the datetime column as the index
    df.set_index('datetime', inplace=True)
    # Save the dataframe to a CSV file
    df.to_csv('plotting_data.csv', index = True)
    for i in range(len(args.logs)):
        log_path = args.logs[i]
        os.system(f"python3 main_static.py --logs {log_path} > output_{i}.txt")

    # Read the CSV file
    df = pd.read_csv('plotting_data.csv')

    # Create a figure and two subplots
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()

    # Plot the open column on the first y-axis scale
    ax2.plot(df['open'], label='Open Price', color='orange')
    ax2.set_ylabel('Open Price')

    # Plot the remaining columns on the second y-axis scale
    for column in df.columns[2:]:
        ax1.plot(df[column], label=column)
    ax1.set_ylabel('PnL of strategies')

    # Display the legend
    ax1.axhline(y=0, color='black', linestyle='--')
    ax2.axhline(y=0, color='black', linestyle='--')
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc='upper left')

    len = df.shape[0] - 1
    xticks = [0, len//4, 2*(len//4), 3*(len//4), len]  # Set xticks at the start and end
    ax2.set_xticks(xticks)
    ax2.set_xticklabels([df.loc[0, 'datetime'], df.loc[len//4, 'datetime'], df.loc[2*(len//4), 'datetime'], df.loc[3*(len//4), 'datetime'], df.loc[len, 'datetime']])  # Set labels at the start and end

    # Show the plot
    plt.show()