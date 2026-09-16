import pandas as pd
import os

# =====================================================
# STEP 1 : LOAD DATASETS
# =====================================================

print("=" * 60)
print("LOADING DATASETS...")
print("=" * 60)

energy_df = pd.read_csv("data/raw/energy_dataset.csv")

weather_df = pd.read_csv(
    "data/raw/weather_features.csv",
    sep="\t",
    low_memory=False
)

print("Datasets Loaded Successfully!")

# =====================================================
# STEP 2 : CONVERT TIME
# =====================================================

energy_df["time"] = pd.to_datetime(
    energy_df["time"],
    utc=True,
    format="mixed"
)

weather_df["pasdt_iso"] = pd.to_datetime(
    weather_df["pasdt_iso"],
    utc=True,
    format="mixed",
    errors="coerce"
)

weather_df.rename(columns={"pasdt_iso": "time"}, inplace=True)

# =====================================================
# STEP 3 : CLEAN WEATHER
# =====================================================

weather_df = weather_df.dropna(subset=["time"])

weather_df["city_name"] = weather_df["city_name"].str.strip()

weather_df = weather_df[
    weather_df["city_name"] != "city_name"
]

# =====================================================
# STEP 4 : DROP EMPTY COLUMNS
# =====================================================

energy_df.drop(
    columns=[
        "generation hydro pumped storage aggregated",
        "forecast wind offshore eday ahead"
    ],
    inplace=True,
    errors="ignore"
)

# =====================================================
# STEP 5 : HANDLE MISSING VALUES
# =====================================================

energy_df.ffill(inplace=True)
weather_df.ffill(inplace=True)

# =====================================================
# STEP 6 : FILTER MADRID WEATHER
# =====================================================

weather_df = weather_df[
    weather_df["city_name"] == "Madrid"
]

# Remove duplicate timestamps
weather_df = weather_df.drop_duplicates(
    subset=["time"],
    keep="first"
)

print("\nMadrid Weather Shape :", weather_df.shape)
print("\nMadrid Weather Shape :", weather_df.shape)

# =====================================================
# STEP 7 : MERGE DATASETS
# =====================================================

merged_df = pd.merge(
    energy_df,
    weather_df,
    on="time",
    how="inner"
)

print("\nMerged Dataset Shape :", merged_df.shape)

# =====================================================
# STEP 8 : CREATE TIME FEATURES
# =====================================================

merged_df["hour"] = merged_df["time"].dt.hour

merged_df["day"] = merged_df["time"].dt.day

merged_df["month"] = merged_df["time"].dt.month

merged_df["year"] = merged_df["time"].dt.year

merged_df["weekday"] = merged_df["time"].dt.day_name()

merged_df["is_weekend"] = (
    merged_df["time"].dt.weekday >= 5
).astype(int)

# =====================================================
# STEP 9 : SAVE DATASET
# =====================================================

os.makedirs("data/processed", exist_ok=True)

merged_df.to_csv(
    "data/processed/cleaned_energy_weather.csv",
    index=False
)

print("\nDataset Saved Successfully!")

print("\nLocation:")
print("data/processed/cleaned_energy_weather.csv")

print("\nFinal Dataset Shape :", merged_df.shape)

print("\nColumns:")
print(merged_df.columns)

print("\n")
print("=" * 60)
print("PREPROCESSING COMPLETED SUCCESSFULLY")
print("=" * 60)



