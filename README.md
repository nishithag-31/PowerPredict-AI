# PowerPredict AI

## Intelligent Energy Demand Forecasting for Smart Cities

PowerPredict AI is an end-to-end machine learning and MLOps system for forecasting electricity demand using historical energy and weather data.

The system combines an XGBoost regression model with explainable AI, model monitoring, data-drift detection, automated retraining, experiment tracking, workflow orchestration, and a web-based dashboard.

## Key Features

* ⚡ Energy demand forecasting using XGBoost
* 🌦️ Historical energy and weather data processing
* 🔍 Explainable AI using SHAP
* 📊 Model performance monitoring
* 📉 Data drift detection using Population Stability Index (PSI)
* 🔄 Automated model retraining when drift is detected
* 🛡️ Model performance gate for accepting or rejecting retrained models
* 🧪 MLflow experiment and model tracking
* 🔁 Prefect-based MLOps workflow orchestration
* 🌐 Flask REST API for model prediction
* 💻 React + Vite dashboard
* ⚙️ GitHub Actions CI for automated Python syntax checks
* 📁 Git/GitHub version control

## Dataset

The project uses historical energy and weather data containing:

* **35,064 records**
* **49 features**
* Energy generation and load-related variables
* Weather variables including temperature, humidity, pressure, and wind speed
* Time-based features such as hour, day, month, weekday, and weekend indicator

## Machine Learning Model

The forecasting model uses **XGBoost Regressor**, which is suitable for structured/tabular data and can model nonlinear relationships between energy demand, weather conditions, renewable generation, and time-related features.

### Model Features

The production prediction pipeline uses:

* Generation solar
* Generation wind onshore
* Forecast solar day ahead
* Forecast wind onshore day ahead
* Temperature
* Humidity
* Pressure
* Wind speed
* Hour
* Day
* Month
* Weekday
* Weekend indicator

## Explainable AI

SHAP (SHapley Additive exPlanations) is used to explain individual predictions.

For each prediction, the system calculates feature contributions so that users can understand which input features influenced the predicted energy demand.

## MLOps Pipeline

The project implements an automated MLOps workflow:

```text
Energy + Weather Data
        ↓
Data Processing
        ↓
XGBoost Model
        ↓
MLflow Tracking
        ↓
Model Evaluation
        ↓
PSI Drift Detection
        ↓
Drift Detected?
     ↙       ↘
   No         Yes
   ↓           ↓
Finish     Retraining
               ↓
        Performance Gate
          ↙          ↘
      Accepted      Rejected
         ↓             ↓
   Production       Keep Existing
      Model            Model
```

Prefect is used to orchestrate the drift detection and automated retraining workflow.

## Model Performance

The currently verified production-model evaluation is:

| Metric |   Value |
| ------ | ------: |
| MAE    | 1109.19 |
| RMSE   | 1612.51 |
| R²     |  0.8753 |

The project also retains previously reported dashboard/poster metrics separately; these should not be confused with the current verified evaluation.

## Technology Stack

### Machine Learning

* Python
* Pandas
* NumPy
* Scikit-learn
* XGBoost
* SHAP

### MLOps

* MLflow
* Prefect
* Population Stability Index (PSI)
* GitHub Actions

### Backend

* Flask
* Flask-CORS
* Joblib

### Frontend

* React
* Vite
* Tailwind CSS

### Version Control

* Git
* GitHub

## Project Structure

```text
PowerPredict-AI/
│
├── app.py
├── requirements.txt
├── .gitignore
├── README.md
│
├── data/
│   └── processed/
│       └── cleaned_energy_weather.csv
│
├── models/
│   └── xgboost_energy_model.pkl
│
├── src/
│   ├── models/
│   │   ├── train_model.py
│   │   ├── retrain_model.py
│   │   └── mlflow_train.py
│   │
│   └── monitoring/
│       ├── drift_detection.py
│       ├── automated_pipeline.py
│       └── prefect_pipeline.py
│
├── frontend/
│   └── ...
│
└── .github/
    └── workflows/
        └── ci.yml
```

## Running the Project

### Backend

```bash
python app.py
```

The Flask API runs on:

```text
http://127.0.0.1:5000
```

### Frontend

From the frontend directory:

```bash
npm run dev
```

The React dashboard runs on:

```text
http://localhost:5173
```

### MLflow

```bash
mlflow ui --port 5002 --workers 1
```

MLflow is available at:

```text
http://127.0.0.1:5002
```

### Prefect MLOps Pipeline

```bash
python src/monitoring/prefect_pipeline.py
```

The workflow performs drift detection and triggers automated retraining when the configured drift condition is met.

## Model Deployment

The trained XGBoost model is loaded by the Flask backend and exposed through a REST API. The React dashboard communicates with the Flask API to obtain predictions and explainable AI results.

## CI/CD

GitHub Actions is configured to automatically check the Python files for syntax errors whenever code is pushed to the repository.

## Project Status

**Working prototype completed.**

The current system includes functional prediction, SHAP explainability, energy-demand visualization, renewable analysis, model monitoring, PSI-based drift detection, MLflow tracking, Prefect orchestration, automated retraining with a performance gate, Flask API deployment, React dashboard integration, and GitHub Actions CI.
