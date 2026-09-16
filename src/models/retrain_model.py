import os
import numpy as np
import pandas as pd
import joblib
import mlflow
import mlflow.xgboost

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

from xgboost import XGBRegressor


# ==========================================================
# POWERPREDICT AI
# AUTOMATED MODEL RETRAINING + PERFORMANCE GATE
# ==========================================================

print("=" * 60)
print("POWERPREDICT AI")
print("AUTOMATED MODEL RETRAINING")
print("=" * 60)


# ==========================================================
# 1. PATHS
# ==========================================================

DATA_PATH = "data/processed/cleaned_energy_weather.csv"

CURRENT_MODEL_PATH = "models/xgboost_energy_model.pkl"

RETRAINED_MODEL_PATH = "models/xgboost_energy_model_retrained.pkl"


# ==========================================================
# 2. LOAD DATASET
# ==========================================================

df = pd.read_csv(DATA_PATH)

print("\nDataset Loaded Successfully!")
print("Dataset Shape:", df.shape)


# ==========================================================
# 3. FEATURES
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
# 4. CONVERT WEEKDAY
# ==========================================================

weekday_mapping = {
    "Monday": 0,
    "Tuesday": 1,
    "Wednesday": 2,
    "Thursday": 3,
    "Friday": 4,
    "Saturday": 5,
    "Sunday": 6
}

if df["weekday"].dtype == "object":
    df["weekday"] = df["weekday"].map(weekday_mapping)


# ==========================================================
# 5. CLEAN DATA
# ==========================================================

df = df[features + [target]].dropna()

print("Usable Records:", len(df))


# ==========================================================
# 6. PREPARE X AND Y
# ==========================================================

X = df[features]
y = df[target]


# ==========================================================
# 7. TRAIN / TEST SPLIT
# ==========================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

print("Training Samples:", len(X_train))
print("Testing Samples:", len(X_test))


# ==========================================================
# 8. LOAD CURRENT PRODUCTION MODEL
# ==========================================================

if not os.path.exists(CURRENT_MODEL_PATH):

    print("\nWARNING: Current production model not found.")

    current_model = None

else:

    current_model = joblib.load(
        CURRENT_MODEL_PATH
    )

    print("\nCurrent Production Model Loaded!")


# ==========================================================
# 9. EVALUATE CURRENT MODEL
# ==========================================================

if current_model is not None:

    current_predictions = current_model.predict(X_test)

    current_mae = mean_absolute_error(
        y_test,
        current_predictions
    )

    current_rmse = np.sqrt(
        mean_squared_error(
            y_test,
            current_predictions
        )
    )

    current_r2 = r2_score(
        y_test,
        current_predictions
    )

    print("\n" + "=" * 40)
    print("CURRENT MODEL PERFORMANCE")
    print("=" * 40)

    print(f"MAE  : {current_mae:.2f}")
    print(f"RMSE : {current_rmse:.2f}")
    print(f"R2   : {current_r2:.4f}")


# ==========================================================
# 10. START MLFLOW
# ==========================================================

mlflow.set_tracking_uri("sqlite:///mlflow.db")

mlflow.set_experiment(
    "PowerPredict_AI_Retraining"
)


with mlflow.start_run():

    # ======================================================
    # 11. TRAIN NEW MODEL
    # ======================================================

    print("\nTraining New XGBoost Model...")

    new_model = XGBRegressor(

        n_estimators=300,

        learning_rate=0.05,

        max_depth=6,

        random_state=42

    )

    new_model.fit(
        X_train,
        y_train
    )

    print("Retraining Completed!")


    # ======================================================
    # 12. PREDICT WITH NEW MODEL
    # ======================================================

    new_predictions = new_model.predict(
        X_test
    )


    # ======================================================
    # 13. EVALUATE NEW MODEL
    # ======================================================

    new_mae = mean_absolute_error(
        y_test,
        new_predictions
    )

    new_rmse = np.sqrt(
        mean_squared_error(
            y_test,
            new_predictions
        )
    )

    new_r2 = r2_score(
        y_test,
        new_predictions
    )


    print("\n" + "=" * 40)
    print("NEW MODEL PERFORMANCE")
    print("=" * 40)

    print(f"MAE  : {new_mae:.2f}")
    print(f"RMSE : {new_rmse:.2f}")
    print(f"R2   : {new_r2:.4f}")


    # ======================================================
    # 14. LOG PARAMETERS
    # ======================================================

    mlflow.log_param(
        "model",
        "XGBoost"
    )

    mlflow.log_param(
        "n_estimators",
        300
    )

    mlflow.log_param(
        "learning_rate",
        0.05
    )

    mlflow.log_param(
        "max_depth",
        6
    )


    # ======================================================
    # 15. LOG NEW MODEL METRICS
    # ======================================================

    mlflow.log_metric(
        "MAE",
        new_mae
    )

    mlflow.log_metric(
        "RMSE",
        new_rmse
    )

    mlflow.log_metric(
        "R2",
        new_r2
    )


    # ======================================================
    # 16. PERFORMANCE GATE
    # ======================================================

    print("\n" + "=" * 60)
    print("MODEL PERFORMANCE GATE")
    print("=" * 60)


    if current_model is None:

        print(
            "No existing model found."
        )

        model_accepted = True

    else:

        # New model must improve all three metrics

        model_accepted = (

            new_mae < current_mae

            and

            new_rmse < current_rmse

            and

            new_r2 > current_r2

        )


    # ======================================================
    # 17. ACCEPT OR REJECT MODEL
    # ======================================================

    if model_accepted:

        print("\n✅ NEW MODEL ACCEPTED!")

        print(
            "The retrained model performs better."
        )


        # Save retrained model

        joblib.dump(
            new_model,
            RETRAINED_MODEL_PATH
        )

        print(
            "\nNew model saved at:"
        )

        print(
            RETRAINED_MODEL_PATH
        )


        # Replace production model

        joblib.dump(
            new_model,
            CURRENT_MODEL_PATH
        )

        print(
            "\n✅ Production model updated!"
        )


        mlflow.log_param(
            "model_status",
            "ACCEPTED"
        )


    else:
        print("\nNEW MODEL REJECTED!")

        print(
            "The retrained model does not improve "
            "the current production model."
        )

        # Save rejected model for analysis

        joblib.dump(
            new_model,
            RETRAINED_MODEL_PATH
        )

        print(
            "\nRejected model saved at:"
        )

        print(
            RETRAINED_MODEL_PATH
        )


        print(
            "\nExisting production model retained."
        )


        mlflow.log_param(
            "model_status",
            "REJECTED"
        )


    # ======================================================
    # 18. LOG MODEL TO MLFLOW
    # ======================================================

    mlflow.xgboost.log_model(
        xgb_model=new_model,
        name="PowerPredict_Retrained_Model"
    )


# ==========================================================
# 19. COMPLETION
# ==========================================================

print("\n" + "=" * 60)
print("AUTOMATED RETRAINING PROCESS COMPLETED")
print("=" * 60)