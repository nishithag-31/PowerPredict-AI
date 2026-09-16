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

if drift_process.returncode != 0:

    print("\n❌ Drift detection failed.")

    if drift_process.stderr:
        print(drift_process.stderr)

    sys.exit(1)


# ==========================================================
# STEP 2: CHECK DRIFT STATUS
# ==========================================================

drift_output = drift_process.stdout


if "Overall Status: Significant Drift" in drift_output:

    print("\n⚠️ Significant Drift Detected!")
    print("Starting automated model retraining...")


elif "Overall Status: Moderate Drift" in drift_output:

    print("\n🟡 Moderate Drift Detected!")
    print("Starting automated model retraining...")


else:

    print("\n🟢 No Significant Drift Detected!")
    print("Retraining is not required.")

    print("\n" + "=" * 60)
    print("AUTOMATED MLOPS PIPELINE COMPLETED")
    print("=" * 60)

    sys.exit(0)


# ==========================================================
# STEP 3: AUTOMATED RETRAINING
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

    print("\n❌ Automated retraining failed.")

    if retrain_process.stderr:
        print(retrain_process.stderr)

    sys.exit(1)


if "NEW MODEL ACCEPTED" in retrain_process.stdout:

    print("\n" + "=" * 60)
    print("✅ NEW MODEL DEPLOYED")
    print("=" * 60)

    print(
        "\nThe retrained model performed better "
        "than the existing production model."
    )


elif "NEW MODEL REJECTED" in retrain_process.stdout:

    print("\n" + "=" * 60)
    print("❌ NEW MODEL REJECTED")
    print("=" * 60)

    print(
        "\nThe retrained model did not improve "
        "the production model."
    )

    print(
        "\n✅ Existing production model retained."
    )


else:

    print("\n⚠️ Could not determine model decision.")


# ==========================================================
# FINAL STATUS
# ==========================================================

print("\n" + "=" * 60)
print("AUTOMATED MLOPS PIPELINE COMPLETED")
print("=" * 60)