# ============================================================
# PowerPredict AI
# Intelligent Energy Demand Forecasting
# ============================================================


# ============================================================
# IMPORT REQUIRED LIBRARIES
# ============================================================

# Import Flask to create the backend REST API.
from flask import Flask, request, jsonify

# Import CORS to allow the React frontend to communicate
# with the Flask backend.
from flask_cors import CORS

# Import joblib to load the trained XGBoost model.
import joblib

# Import pandas for creating and processing DataFrames.
import pandas as pd

# Import numpy for numerical calculations.
import numpy as np

# Import SHAP for model explainability.
import shap

# Import datetime to record prediction timestamps.
from datetime import datetime


# ============================================================
# CREATE FLASK APPLICATION
# ============================================================

# Create the Flask application.
app = Flask(__name__)

# Enable CORS for the React frontend.
# This allows requests from localhost:5173 to reach Flask.
CORS(
    app,
    resources={
        r"/*": {
            "origins": [
                "http://localhost:5173",
                "http://127.0.0.1:5173"
            ]
        }
    },
    supports_credentials=False
)


# ============================================================
# FILE PATHS
# ============================================================

# Path to the processed energy and weather dataset.
DATA_PATH = "data/processed/cleaned_energy_weather.csv"

# Path to the trained XGBoost model.
MODEL_PATH = "models/xgboost_energy_model.pkl"


# ============================================================
# MODEL FEATURES
# ============================================================

# These feature names MUST match the feature names used
# during model training.
FEATURES = [
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


# ============================================================
# LOAD TRAINED MODEL
# ============================================================

# Load the trained XGBoost model from the models folder.
model = joblib.load(MODEL_PATH)

# Create a SHAP TreeExplainer for explaining XGBoost predictions.
explainer = shap.TreeExplainer(model)


# ============================================================
# PREDICTION HISTORY
# ============================================================

# Store predictions generated during the current Flask session.
# This is useful for dynamic monitoring.
prediction_history = []


# ============================================================
# HOME ROUTE
# ============================================================

# Create the home API endpoint.
@app.route("/", methods=["GET"])
def home():

    # Return a simple message confirming that the API is running.
    return jsonify({
        "message": "Welcome to PowerPredict AI API 🚀",
        "status": "API Connected"
    })


# ============================================================
# PREDICTION ROUTE
# ============================================================

# Create the prediction API endpoint.
@app.route("/predict", methods=["POST"])
def predict():

    # Start exception handling.
    try:

        # Get JSON data sent by the React frontend.
        data = request.get_json()

        # Check whether the frontend actually sent data.
        if not data:
            return jsonify({
                "error": "No input data received."
            }), 400

        # Create a dictionary using the exact model feature names.
        input_data = {}

        # Process every feature required by the model.
        for feature in FEATURES:

            # Get the feature value from the frontend.
            value = data.get(feature, 0)

            # Convert the value to a numeric value.
            # Invalid or empty values become 0.
            try:
                value = float(value)
            except (TypeError, ValueError):
                value = 0.0

            # Store the cleaned value.
            input_data[feature] = value

        # Create a DataFrame containing one prediction row.
        input_df = pd.DataFrame([input_data])

        # Force the DataFrame into the exact training feature order.
        input_df = input_df[FEATURES]

        # Generate the electricity demand prediction.
        prediction = model.predict(input_df)

        # Calculate SHAP values for the prediction.
        shap_values = explainer.shap_values(input_df)

        # Handle SHAP Explanation objects if returned.
        if hasattr(shap_values, "values"):
            shap_values = shap_values.values

        # Convert the first prediction row into a simple array.
        shap_values = np.asarray(shap_values)

        # Handle one-dimensional SHAP output.
        if shap_values.ndim == 1:
            shap_row = shap_values

        # Handle two-dimensional SHAP output.
        else:
            shap_row = shap_values[0]

        # Create a dictionary to store feature explanations.
        explanation = {}

        # Match every feature with its SHAP value.
        for feature, value in zip(FEATURES, shap_row):

            # Convert the SHAP value into a normal Python float.
            explanation[feature] = round(float(value), 4)

        # Convert the prediction into a normal Python float.
        prediction_value = float(prediction[0])

        # Store the prediction for monitoring.
        prediction_history.append({
            "timestamp": datetime.now().isoformat(),
            "prediction": prediction_value
        })

        # Return prediction and SHAP explanation to React.
        return jsonify({
            "prediction": round(prediction_value, 2),
            "explanation": explanation
        })

    # Handle any prediction error.
    except Exception as e:

        # Print the error in the Flask terminal.
        print("❌ Prediction Error:", str(e))

        # Send the error back to React.
        return jsonify({
            "error": str(e)
        }), 500


# ============================================================
# MODEL MONITORING ROUTE
# ============================================================

# Create the model monitoring endpoint.
@app.route("/monitoring", methods=["GET"])
def monitoring():

    # Calculate the number of predictions generated
    # during the current backend session.
    prediction_count = len(prediction_history)

    # Set latest prediction to None when no prediction exists.
    latest_prediction = None

    # Get the latest prediction when available.
    if prediction_count > 0:
        latest_prediction = prediction_history[-1]["prediction"]

    # Calculate the average prediction when predictions exist.
    average_prediction = None

    if prediction_count > 0:

        # Extract all prediction values.
        values = [
            item["prediction"]
            for item in prediction_history
        ]

        # Calculate the average.
        average_prediction = sum(values) / len(values)

    # Return monitoring information.
    #
    # MAE, RMSE and R² below represent the model's
    # validated test-set performance.
    #
    # They should NOT be changed using a single new prediction
    # because there is no actual demand value available yet.
    return jsonify({

        # Model name.
        "model": "XGBoost",

        # Validated model performance.
        "mae": 260.95,
        "rmse": 386.41,
        "r2": 0.9928,

        # Model status.
        "status": "Healthy",

        # Dynamic prediction monitoring.
        "prediction_count": prediction_count,
        "latest_prediction": (
            round(latest_prediction, 2)
            if latest_prediction is not None
            else None
        ),
        "average_prediction": (
            round(average_prediction, 2)
            if average_prediction is not None
            else None
        )
    })


# ============================================================
# DATA DRIFT ROUTE
# ============================================================

# Create the data drift endpoint.
@app.route("/drift", methods=["POST", "OPTIONS"])
def drift():

    # Handle the browser's CORS preflight request.
    if request.method == "OPTIONS":

        # Return a successful response for preflight.
        return jsonify({
            "status": "OK"
        }), 200

    # Start exception handling.
    try:

        # Get the current input sent by React.
        current_input = request.get_json()

        # Check whether input data was received.
        if not current_input:
            return jsonify({
                "error": "No input data received."
            }), 400

        # Load the historical reference dataset.
        df = pd.read_csv(DATA_PATH)

        # Check that the required time column exists.
        if "time" not in df.columns:
            return jsonify({
                "error": "Dataset does not contain a 'time' column."
            }), 500

        # Convert the time column into datetime values.
        time_values = pd.to_datetime(
            df["time"],
            errors="coerce"
        )

        # Create the reference dataset using model features.
        reference_data = df[FEATURES].copy()

        # Recalculate weekday from the original timestamp.
        reference_data["weekday"] = time_values.dt.weekday

        # Convert all features to numeric values.
        for feature in FEATURES:

            # Convert invalid values into NaN.
            reference_data[feature] = pd.to_numeric(
                reference_data[feature],
                errors="coerce"
            )

        # Remove incomplete historical rows.
        reference_data = reference_data.dropna()

        # Create one-row current input DataFrame.
        current_data = pd.DataFrame([{

            # Convert every current feature into a number.
            feature: pd.to_numeric(
                current_input.get(feature, 0),
                errors="coerce"
            )

            # Process all model features.
            for feature in FEATURES
        }])

        # Replace invalid current values with zero.
        current_data = current_data.fillna(0)

        # --------------------------------------------------------
        # REFERENCE VS RECENT DATA DRIFT
        # --------------------------------------------------------

        # Use the latest historical records as the current batch.
        recent_data = reference_data.tail(1000).copy()

        # Create a list to store the drift results.
        results = []

        # Calculate PSI between two distributions.
        def calculate_psi(reference, current, bins=10):

            # Convert both datasets into NumPy arrays.
            reference = np.asarray(reference, dtype=float)
            current = np.asarray(current, dtype=float)

            # Remove invalid values.
            reference = reference[np.isfinite(reference)]
            current = current[np.isfinite(current)]

            # Return zero if either dataset is empty.
            if len(reference) == 0 or len(current) == 0:
                return 0.0

            # Create percentile-based bins using reference data.
            breakpoints = np.percentile(
                reference,
                np.linspace(0, 100, bins + 1)
            )

            # Remove duplicate bin boundaries.
            breakpoints = np.unique(breakpoints)

            # If there are not enough unique bins, no drift can be calculated.
            if len(breakpoints) < 2:
                return 0.0

            # Calculate reference distribution.
            reference_counts, _ = np.histogram(
                reference,
                bins=breakpoints
            )

            # Calculate current distribution.
            current_counts, _ = np.histogram(
                current,
                bins=breakpoints
            )

            # Convert counts into percentages.
            reference_percentage = (
                reference_counts / len(reference)
            )

            current_percentage = (
                current_counts / len(current)
            )

            # Prevent division by zero and log(0).
            reference_percentage = np.where(
                reference_percentage == 0,
                0.0001,
                reference_percentage
            )

            current_percentage = np.where(
                current_percentage == 0,
                0.0001,
                current_percentage
            )

            # Calculate PSI.
            psi = np.sum(
                (
                    current_percentage
                    - reference_percentage
                )
                *
                np.log(
                    current_percentage
                    /
                    reference_percentage
                )
            )

            # Return the PSI value.
            return float(psi)

        # Calculate drift for every model feature.
        for feature in FEATURES:

            # Get historical reference values.
            reference_values = reference_data[feature].values

            # Get recent values.
            current_values = recent_data[feature].values

            # Calculate PSI.
            psi = calculate_psi(
                reference_values,
                current_values
            )

            # Determine drift status.
            if psi < 0.10:

                # No significant distribution change.
                status = "No Drift"

            elif psi < 0.25:

                # Moderate distribution change.
                status = "Moderate Drift"

            else:

                # Significant distribution change.
                status = "Significant Drift"

            # Store the feature result.
            results.append({
                "feature": feature,
                "psi": round(psi, 4),
                "status": status
            })

        # Count significant drift features.
        significant = sum(
            result["status"] == "Significant Drift"
            for result in results
        )

        # Count moderate drift features.
        moderate = sum(
            result["status"] == "Moderate Drift"
            for result in results
        )

        # Determine the overall drift status.
        if significant > 0:

            # At least one feature has significant drift.
            overall_status = "Drift Detected"

        elif moderate > 0:

            # At least one feature has moderate drift.
            overall_status = "Moderate Drift"

        else:

            # No feature has meaningful drift.
            overall_status = "Healthy"

        # Return the complete drift information to React.
        return jsonify({

            # Overall drift status.
            "status": overall_status,

            # Number of significant features.
            "significant_features": significant,

            # Number of moderate features.
            "moderate_features": moderate,

            # Feature-by-feature drift results.
            "features": results

        })

    # Handle drift calculation errors.
    except Exception as e:

        # Print the error in the Flask terminal.
        print("❌ Drift Error:", str(e))

        # Return the error to React.
        return jsonify({
            "error": str(e)
        }), 500


# ============================================================
# RENEWABLE ENERGY ROUTE
# ============================================================

# Create the renewable energy endpoint.
@app.route("/renewable", methods=["POST", "OPTIONS"])
def renewable():

    # Handle browser CORS preflight requests.
    if request.method == "OPTIONS":

        # Return successful preflight response.
        return jsonify({
            "status": "OK"
        }), 200

    # Start exception handling.
    try:

        # Get current prediction input from React.
        data = request.get_json()

        # Check whether data was received.
        if not data:
            return jsonify({
                "error": "No input data received."
            }), 400

        # Read current solar generation.
        solar = float(
            data.get("generation solar", 0)
        )

        # Read current onshore wind generation.
        wind_onshore = float(
            data.get("generation wind onshore", 0)
        )

        # Read offshore wind generation.
        wind_offshore = float(
            data.get("generation wind offshore", 0)
        )

        # Calculate total wind generation.
        total_wind = (
            wind_onshore
            +
            wind_offshore
        )

        # Calculate total renewable generation.
        total_renewable = (
            solar
            +
            total_wind
        )

        # --------------------------------------------------------
        # PREPARE MODEL INPUT
        # --------------------------------------------------------

        # Create a clean dictionary containing model features.
        input_data = {}

        # Process every required model feature.
        for feature in FEATURES:

            # Read the current value.
            value = data.get(feature, 0)

            # Convert to numeric.
            try:
                value = float(value)
            except (TypeError, ValueError):
                value = 0.0

            # Store the cleaned value.
            input_data[feature] = value

        # Create DataFrame for the model.
        input_df = pd.DataFrame([
            input_data
        ])

        # Force exact feature order.
        input_df = input_df[FEATURES]

        # Predict total electricity demand.
        prediction = model.predict(input_df)

        # Convert model prediction into float.
        total_load = float(
            prediction[0]
        )

        # Calculate renewable energy share.
        if total_load > 0:

            renewable_share = (
                total_renewable
                /
                total_load
            ) * 100

        else:

            renewable_share = 0

        # Return renewable energy information.
        return jsonify({

            # Current solar generation.
            "solar_generation": round(
                solar,
                2
            ),

            # Current onshore wind generation.
            "wind_onshore_generation": round(
                wind_onshore,
                2
            ),

            # Current offshore wind generation.
            "wind_offshore_generation": round(
                wind_offshore,
                2
            ),

            # Total wind generation.
            "total_wind_generation": round(
                total_wind,
                2
            ),

            # Total renewable generation.
            "total_renewable_generation": round(
                total_renewable,
                2
            ),

            # Current model-predicted load.
            "total_load": round(
                total_load,
                2
            ),

            # Renewable percentage of predicted load.
            "renewable_share": round(
                renewable_share,
                2
            )
        })

    # Handle renewable energy errors.
    except Exception as e:

        # Print error in Flask terminal.
        print(
            "❌ Renewable Energy Error:",
            str(e)
        )

        # Return error to React.
        return jsonify({
            "error": str(e)
        }), 500


# ============================================================
# ENERGY DEMAND TREND ROUTE
# ============================================================

# Create the historical energy trend endpoint.
@app.route("/energy-trend", methods=["GET"])
def energy_trend():

    # Start exception handling.
    try:

        # Load the processed energy dataset.
        df = pd.read_csv(DATA_PATH)

        # Convert the time column to datetime.
        df["time"] = pd.to_datetime(
            df["time"],
            errors="coerce"
        )

        # Remove rows with invalid timestamps.
        df = df.dropna(
            subset=["time"]
        )

        # Sort records chronologically.
        df = df.sort_values(
            "time"
        )

        # Take the latest 30 historical records.
        recent_data = df.tail(30)

        # Create the response list.
        trend = []

        # Process every historical record.
        for _, row in recent_data.iterrows():

            # Add timestamp and actual demand.
            trend.append({

                # Convert timestamp into ISO format.
                "time": row["time"].isoformat(),

                # Convert demand into float.
                "demand": float(
                    row["total load actual"]
                )
            })

        # Return historical demand trend.
        return jsonify(trend)

    # Handle trend errors.
    except Exception as e:

        # Print error in Flask terminal.
        print(
            "❌ Energy Trend Error:",
            str(e)
        )

        # Return error to React.
        return jsonify({
            "error": str(e)
        }), 500


# ============================================================
# RUN FLASK SERVER
# ============================================================

# Start the Flask development server only when this
# file is executed directly.
if __name__ == "__main__":

    # Start Flask on port 5000.
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )