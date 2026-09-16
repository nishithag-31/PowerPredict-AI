import mlflow
import mlflow.sklearn
import mlflow.xgboost

import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

from xgboost import XGBRegressor

print("="*60)
print("POWERPREDICT AI")
print("MLFLOW MODEL TRAINING")
print("="*60)

# -------------------------------------------------
# Load Dataset
# -------------------------------------------------

df = pd.read_csv(
    "data/processed/cleaned_energy_weather.csv"
)

print("\nDataset Loaded!")

# -------------------------------------------------
# Prepare Features
# -------------------------------------------------

df = df.drop(columns=[
    "time",
    "weather_main",
    "weather_description",
    "weather_icon",
    "weekday",
    "city_name"
])

target = "total load actual"

X = df.drop(columns=[target])
y = df[target]

# -------------------------------------------------
# Train Test Split
# -------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

print("Train Samples :", len(X_train))
print("Test Samples :", len(X_test))

# -------------------------------------------------
# MLflow
# -------------------------------------------------

mlflow.set_experiment("PowerPredict_AI")

with mlflow.start_run():

    model = XGBRegressor(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=6,
        random_state=42
    )

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    mae = mean_absolute_error(
        y_test,
        predictions
    )

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

    # -------------------------------
    # Log Parameters
    # -------------------------------

    mlflow.log_param("Model", "XGBoost")
    mlflow.log_param("Estimators", 200)
    mlflow.log_param("Learning Rate", 0.05)
    mlflow.log_param("Max Depth", 6)

    # -------------------------------
    # Log Metrics
    # -------------------------------

    mlflow.log_metric("MAE", mae)
    mlflow.log_metric("RMSE", rmse)
    mlflow.log_metric("R2", r2)

    # -------------------------------
    # Save Model
    # -------------------------------

    mlflow.xgboost.log_model(
    xgb_model=model,
    name="PowerPredict_Model"
)

print("\nTraining Finished!")

print("\nMAE :", round(mae,2))
print("RMSE :", round(rmse,2))
print("R2 :", round(r2,4))
