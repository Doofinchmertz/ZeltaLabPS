import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns

df = pd.read_csv("data/btcusdt_1h_train.csv")
df.drop(['open', 'high', 'low', 'close'], axis=1, inplace=True)
correlation_matrix = df.corr()
plt.figure(figsize=(10, 8))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm')
plt.title('Correlation Heatmap')
plt.show()