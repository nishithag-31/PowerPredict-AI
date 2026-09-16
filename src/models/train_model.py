import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score

from xgboost import XGBRegressor

print("="*60)
print("POWERPREDICT AI")
print("MODEL TRAINING")
print("="*60)

# ==========================================================
# Load Dataset
# ==========================================================

df = pd.read_csv("data/processed/cleaned_energy_weather.csv")

print("\nDataset Loaded Successfully!")
print("Shape :", df.shape)

# ==========================================================
# Select Features
# ==========================================================

features = [

    "generation solar",
    "generation wind onshore",

    "forecast solar day ahead",
    "forecast wind onshore day ahead",

    "temp",
    "humidity",
    "pressure",
    "wind_speed",

    "hour",
    "day",
    "month",
    "weekday",
    "is_weekend"

]

target = "total load actual"

# ==========================================================
# Convert Weekday into Numbers
# ==========================================================

weekday_mapping = {
    "Monday":0,
    "Tuesday":1,
    "Wednesday":2,
    "Thursday":3,
    "Friday":4,
    "Saturday":5,
    "Sunday":6
}

df["weekday"] = df["weekday"].map(weekday_mapping)

# ==========================================================
# Prepare X and y
# ==========================================================

X = df[features]

y = df[target]

# ==========================================================
# Train Test Split
# ==========================================================

X_train, X_test, y_train, y_test = train_test_split(

    X,
    y,
    test_size=0.2,
    random_state=42

)

print("\nTraining Samples :", len(X_train))
print("Testing Samples :", len(X_test))

# ==========================================================
# Build XGBoost Model
# ==========================================================

model = XGBRegressor(

    n_estimators=300,
    learning_rate=0.05,
    max_depth=6,
    random_state=42

)

print("\nTraining Model...")

model.fit(X_train, y_train)

print("Training Completed!")

# ==========================================================
# Prediction
# ==========================================================

predictions = model.predict(X_test)

# ==========================================================
# Evaluation
# ==========================================================

mae = mean_absolute_error(y_test, predictions)


rmse = np.sqrt(
    mean_squared_error(
        y_test,
        predictions
    )
)

r2 = r2_score(
    y_test,
    predictions
)

print("\n==============================")
print("MODEL PERFORMANCE")
print("==============================")

print(f"MAE  : {mae:.2f}")
print(f"RMSE : {rmse:.2f}")
print(f"R²   : {r2:.4f}")

# ==========================================================
# Save Model
# ==========================================================

joblib.dump(
    model,
    "models/xgboost_energy_model.pkl"
)

print("\nModel Saved Successfully!")

print("\nLocation:")
print("models/xgboost_energy_model.pkl")

print("\n==============================")
print("MODEL TRAINING COMPLETED")
print("==============================")