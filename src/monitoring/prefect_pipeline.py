# Import the subprocess module to run our existing Python scripts.
import subprocess

# Import sys so we can use the same Python interpreter from our virtual environment.
import sys

# Import the task decorator from Prefect.
from prefect import task


# Create a Prefect task for running data drift detection.
@task
def run_drift_detection():

    # Run the existing drift detection script using the current Python interpreter.
    process = subprocess.run(
        [
            sys.executable,
            "src/monitoring/drift_detection.py"
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    # Display the output produced by the drift detection script.
    print(process.stdout)

    # Check whether the drift detection script failed.
    if process.returncode != 0:

        # Display the error message if the script failed.
        print(process.stderr)

        # Stop the Prefect task with an error.
        raise RuntimeError("Data drift detection failed.")

    # Return the drift detection output so the Prefect flow can use it.
    return process.stdout

# Create a Prefect task for automated model retraining.
@task
def run_retraining():

    # Run the existing automated retraining script using the current Python interpreter.
    process = subprocess.run(
        [
            sys.executable,
            "src/models/retrain_model.py"
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    # Display the output produced by the retraining script.
    print(process.stdout)

    # Check whether the retraining script failed.
    if process.returncode != 0:

        # Display the error message if the retraining script failed.
        print(process.stderr)

        # Stop the Prefect task with an error.
        raise RuntimeError("Automated model retraining failed.")

    # Return the retraining output.
    return process.stdout

# Import the flow decorator from Prefect.
from prefect import flow


# Create the main PowerPredict AI MLOps Prefect flow.
@flow(name="PowerPredict_AI_MLOps_Pipeline")
def powerpredict_pipeline():

    # Run the data drift detection task first.
    drift_output = run_drift_detection()

    # Check whether significant or moderate drift was detected.
    if (
        "Overall Status: Significant Drift" in drift_output
        or "Overall Status: Moderate Drift" in drift_output
    ):

        # Display a message explaining why retraining will start.
        print("\nDrift detected. Starting automated retraining...")

        # Run the automated retraining task.
        retraining_output = run_retraining()

        # Return the retraining result.
        return retraining_output

    # Display a message when retraining is not required.
    print("\nNo significant drift detected. Retraining is not required.")

    # Return the drift detection result.
    return drift_output


# Run the Prefect flow when this file is executed directly.
if __name__ == "__main__":

    # Start the PowerPredict AI MLOps Prefect pipeline.
    powerpredict_pipeline()