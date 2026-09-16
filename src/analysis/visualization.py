import pandas as pd
import matplotlib.pyplot as plt

# Load dataset
df = pd.read_csv("data/processed/cleaned_energy_weather.csv")

# Convert time column
df["time"] = pd.to_datetime(df["time"])

# -----------------------------------
# 1. Total Load Trend
# -----------------------------------
plt.figure(figsize=(15,5))
plt.plot(df["time"], df["total load actual"])
plt.title("Total Electricity Demand Over Time")
plt.xlabel("Time")
plt.ylabel("MW")
plt.grid(True)
plt.show()

# -----------------------------------
# 2. Hourly Demand Pattern
# -----------------------------------
hourly = df.groupby("hour")["total load actual"].mean()

plt.figure(figsize=(10,5))
plt.plot(hourly.index, hourly.values, marker="o")
plt.title("Average Hourly Electricity Demand")
plt.xlabel("Hour")
plt.ylabel("Average MW")
plt.grid(True)
plt.show()

# -----------------------------------
# 3. Monthly Demand
# -----------------------------------
monthly = df.groupby("month")["total load actual"].mean()

plt.figure(figsize=(10,5))
plt.bar(monthly.index, monthly.values)
plt.title("Average Monthly Electricity Demand")
plt.xlabel("Month")
plt.ylabel("Average MW")
plt.show()

# -----------------------------------
# 4. Solar Generation
# -----------------------------------
solar = df.groupby("month")["generation solar"].mean()

plt.figure(figsize=(10,5))
plt.plot(solar.index, solar.values, marker="o")
plt.title("Average Solar Generation")
plt.xlabel("Month")
plt.ylabel("MW")
plt.grid(True)
plt.show()

# -----------------------------------
# 5. Wind Generation
# -----------------------------------
wind = df.groupby("month")["generation wind onshore"].mean()

plt.figure(figsize=(10,5))
plt.plot(wind.index, wind.values, marker="o")
plt.title("Average Wind Generation")
plt.xlabel("Month")
plt.ylabel("MW")
plt.grid(True)
plt.show()