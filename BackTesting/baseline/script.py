import matplotlib.pyplot as plt
import os

v1_values = []
v2_values = []
output_file = "junk.txt"
max_k = 30
for k in range(20, max_k + 1):
    os.system(f"echo Hello {k}")
    os.system(f"python3 add_indicators.py train {k}")
    os.system(f"python3 add_indicators.py val {k}")
    os.system("python3 normalize_features.py")
    os.system(f"python3 fit_linear_model.py {k} > junk.txt")
    v1 = float(open(output_file).readlines()[0])
    v2 = float(open(output_file).readlines()[1])
    v1_values.append(v1)
    v2_values.append(v2)
    os.system("echo Hello done")

# Plot the graph
plt.plot(range(20, max_k + 1), v1_values, label='training_corr')
# plt.plot(range(20, max_k + 1), v2_values, label='validation_corr')
plt.xlabel('k')
plt.ylabel('Value')
plt.legend()
plt.savefig('variation_with_k.png')
plt.show()

