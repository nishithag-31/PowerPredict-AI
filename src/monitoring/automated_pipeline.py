import subprocess
import sys

print("=" * 60)
print("POWERPREDICT AI")
print("AUTOMATED MLOPS PIPELINE")
print("=" * 60)


# ==========================================================
# STEP 1: DATA DRIFT DETECTION
# ==========================================================

print("\n[1/2] Running Data Drift Detection...")
print("-" * 60)

drift_process = subprocess.run(
    [
        sys.executable,
        "src/monitoring/drift_detection.py"
    ],
    capture_output=True,
    text=True,
    encoding="utf-8",
    errors="replace"
)

print(drift_process.stdout)

# Check whether drift detection script itself failed
if drift_process.returncode != 0:

    print("\nERROR: Data drift detection failed.")
    print(drift_process.stderr)

    print("\n" + "=" * 60)
    print("AUTOMATED MLOPS PIPELINE STOPPED")
    print("=" * 60)

    sys.exit(1)


# ==========================================================
# CHECK DRIFT STATUS
# ==========================================================

drift_output = drift_process.stdout

if "Overall Status: Significant Drift" in drift_output:

    print("\nSignificant Drift Detected!")
    print("Starting automated model retraining...")

elif "Overall Status: Moderate Drift" in drift_output:

    print("\nModerate Drift Detected!")
    print("Starting automated model retraining...")

else:

    print("\nNo Significant Drift Detected!")
    print("Retraining is not required.")

    print("\n" + "=" * 60)
    print("AUTOMATED MLOPS PIPELINE COMPLETED")
    print("=" * 60)

    sys.exit(0)


# ==========================================================
# STEP 2: AUTOMATED RETRAINING
# ==========================================================

print("\n[2/2] Starting Automated Retraining...")
print("-" * 60)

retrain_process = subprocess.run(
    [
        sys.executable,
        "src/models/retrain_model.py"
    ],
    capture_output=True,
    text=True,
    encoding="utf-8",
    errors="replace"
)

print(retrain_process.stdout)


# ==========================================================
# CHECK RETRAINING RESULT
# ==========================================================

if retrain_process.returncode != 0:

    print("\nERROR: Automated retraining failed.")
    print(retrain_process.stderr)

    print("\n" + "=" * 60)
    print("AUTOMATED MLOPS PIPELINE COMPLETED WITH ERRORS")
    print("=" * 60)

    sys.exit(1)


# ==========================================================
# FINAL STATUS
# ==========================================================

print("\nAutomated retraining completed successfully.")

print("\n" + "=" * 60)
print("AUTOMATED MLOPS PIPELINE COMPLETED")
print("=" * 60)