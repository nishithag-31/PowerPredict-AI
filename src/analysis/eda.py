import pandas as pd

print("=" * 60)
print("POWERPREDICT AI")
print("EXPLORATORY DATA ANALYSIS")
print("=" * 60)

# Load cleaned dataset
df = pd.read_csv("data/processed/cleaned_energy_weather.csv")

print("\n✅ Dataset Loaded Successfully!")

print("\nDataset Shape")
print(df.shape)

print("\nColumn Names")
print(df.columns.tolist())

print("\nFirst Five Rows")
print(df.head())

print("\nData Types")
print(df.dtypes)

print("\nMissing Values")
print(df.isnull().sum())

print("\nSummary Statistics")
print(df.describe())

print("\nEDA Step 1 Completed Successfully!")

import matplotlib.pyplot as plt

print("\nGenerating Graphs...")

# ---------------------------------------
# Total Load Trend
# ---------------------------------------

plt.figure(figsize=(15,5))

plt.plot(
    df["total load actual"],
    color="blue"
)

plt.title("Total Electricity Demand")

plt.xlabel("Time")

plt.ylabel("MW")

plt.grid(True)

plt.show()