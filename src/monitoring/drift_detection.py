import pandas as pd
import numpy as np


# ==========================================
# PowerPredict AI - Data Drift Detection
# ==========================================

DATA_PATH = "data/processed/cleaned_energy_weather.csv"

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
    "is_weekend",
]


def calculate_psi(reference, current, bins=10):

    reference = np.asarray(reference, dtype=float)
    current = np.asarray(current, dtype=float)

    reference = reference[np.isfinite(reference)]
    current = current[np.isfinite(current)]

    if len(reference) == 0 or len(current) == 0:
        return 0.0

    breakpoints = np.percentile(
        reference,
        np.linspace(0, 100, bins + 1)
    )

    breakpoints = np.unique(breakpoints)

    if len(breakpoints) < 2:
        return 0.0

    reference_counts, _ = np.histogram(
        reference,
        bins=breakpoints
    )

    current_counts, _ = np.histogram(
        current,
        bins=breakpoints
    )

    reference_percentage = (
        reference_counts / len(reference)
    )

    current_percentage = (
        current_counts / len(current)
    )

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

    psi = np.sum(
        (current_percentage - reference_percentage)
        * np.log(
            current_percentage /
            reference_percentage
        )
    )

    return float(psi)


def detect_drift():

    print("=" * 60)
    print("POWERPREDICT AI")
    print("DATA DRIFT DETECTION")
    print("=" * 60)

    # ==========================================
    # Load dataset
    # ==========================================

    df = pd.read_csv(DATA_PATH)

    print("\nDataset Loaded!")
    print("Dataset Shape:", df.shape)

    # ==========================================
    # Select model features
    # ==========================================

    data = df[FEATURES].copy()

    # ==========================================
    # Recreate weekday from time
    # ==========================================

    time_values = pd.to_datetime(
        df["time"],
        errors="coerce"
    )

    data["weekday"] = time_values.dt.weekday

    # ==========================================
    # Convert features to numeric
    # ==========================================

    for feature in FEATURES:

        data[feature] = pd.to_numeric(
            data[feature],
            errors="coerce"
        )

    # ==========================================
    # Check missing values
    # ==========================================

    print("\nMissing Values:")

    print(
        data.isna()
        .sum()
        .to_string()
    )

    # ==========================================
    # Remove invalid rows
    # ==========================================

    data = data.dropna()

    print("\nUsable Records:", len(data))

    if len(data) == 0:

        print(
            "\nERROR: No usable records after cleaning."
        )

        return

    # ==========================================
    # Split reference and current data
    # ==========================================

    split_index = int(len(data) * 0.7)

    reference_data = data.iloc[:split_index]

    current_data = data.iloc[split_index:]

    print(
        "\nReference Records:",
        len(reference_data)
    )

    print(
        "Current Records:",
        len(current_data)
    )

    # ==========================================
    # Calculate PSI
    # ==========================================

    print("\n" + "-" * 60)
    print("FEATURE DRIFT RESULTS")
    print("-" * 60)

    results = []

    for feature in FEATURES:

        reference = reference_data[feature].values

        current = current_data[feature].values

        psi = calculate_psi(
            reference,
            current
        )

        if psi < 0.10:

            status = "No Drift"

        elif psi < 0.25:

            status = "Moderate Drift"

        else:

            status = "Significant Drift"

        results.append({
            "feature": feature,
            "psi": round(psi, 4),
            "status": status
        })

        print(
            f"{feature:40} "
            f"PSI: {psi:.4f} "
            f"-> {status}"
        )

    # ==========================================
    # Overall status
    # ==========================================

    results_df = pd.DataFrame(results)

    significant = (
        results_df["status"]
        == "Significant Drift"
    ).sum()

    moderate = (
        results_df["status"]
        == "Moderate Drift"
    ).sum()

    if significant > 0:

        overall_status = "Drift Detected"

    elif moderate > 0:

        overall_status = "Moderate Drift"

    else:

        overall_status = "Healthy"

    # ==========================================
    # Display final result
    # ==========================================

    print("\n" + "=" * 60)
    print("OVERALL DRIFT STATUS")
    print("=" * 60)

    print(
        "Significant Drift Features:",
        significant
    )

    print(
        "Moderate Drift Features:",
        moderate
    )

    print(
        "Overall Status:",
        overall_status
    )

    print("=" * 60)


# ==========================================
# Run the detector
# ==========================================

if __name__ == "__main__":
    detect_drift()