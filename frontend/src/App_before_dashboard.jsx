import { useEffect, useState } from "react";
import "./App.css";

function App() {
  // ==============================
  // Form Data
  // ==============================

  const [formData, setFormData] = useState({
    generation_solar: "",
    generation_wind_onshore: "",
    forecast_solar_day_ahead: "",
    forecast_wind_onshore_day_ahead: "",
    temp: "",
    humidity: "",
    pressure: "",
    wind_speed: "",
    hour: "",
    day: "",
    month: "",
    weekday: "",
    is_weekend: "",
  });

  // ==============================
  // Prediction State
  // ==============================

  const [prediction, setPrediction] = useState(null);
  const [explanation, setExplanation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // ==============================
  // Monitoring State
  // ==============================

  const [monitoring, setMonitoring] = useState(null);
  const [driftData, setDriftData] = useState(null);

  // ==============================
  // Model Monitoring
  // ==============================

  useEffect(() => {
    fetch("http://127.0.0.1:5000/monitoring")
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to load monitoring data");
        }

        return response.json();
      })
      .then((data) => {
        setMonitoring(data);
      })
      .catch((err) => {
        console.error("Monitoring error:", err);
      });
  }, []);

  // ==============================
  // Data Drift Monitoring
  // ==============================

  useEffect(() => {
    fetch("http://127.0.0.1:5000/drift")
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to load drift data");
        }

        return response.json();
      })
      .then((data) => {
        setDriftData(data);
      })
      .catch((err) => {
        console.error("Drift monitoring error:", err);
      });
  }, []);

  // ==============================
  // Handle Input Changes
  // ==============================

  const handleChange = (e) => {
    const { name, value } = e.target;

    setFormData((previousData) => ({
      ...previousData,
      [name]: value,
    }));
  };

  // ==============================
  // Prediction
  // ==============================

  const handlePredict = async (e) => {
    e.preventDefault();

    setLoading(true);
    setPrediction(null);
    setExplanation(null);
    setError("");

    try {
      const response = await fetch("http://127.0.0.1:5000/predict", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },

        body: JSON.stringify({
          "generation solar": Number(formData.generation_solar),

          "generation wind onshore": Number(
            formData.generation_wind_onshore
          ),

          "forecast solar day ahead": Number(
            formData.forecast_solar_day_ahead
          ),

          "forecast wind onshore day ahead": Number(
            formData.forecast_wind_onshore_day_ahead
          ),

          temp: Number(formData.temp),

          humidity: Number(formData.humidity),

          pressure: Number(formData.pressure),

          wind_speed: Number(formData.wind_speed),

          hour: Number(formData.hour),

          day: Number(formData.day),

          month: Number(formData.month),

          weekday: Number(formData.weekday),

          is_weekend: Number(formData.is_weekend),
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Prediction failed");
      }

      // Prediction value
      setPrediction(data.prediction);

      // SHAP explanation
      setExplanation(data.explanation || null);
    } catch (err) {
      console.error("Prediction error:", err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // ==============================
  // Format Feature Name
  // ==============================

  const formatFeatureName = (feature) => {
    return feature
      .replaceAll("_", " ")
      .replaceAll("generation ", "Generation ")
      .replaceAll("forecast ", "Forecast ")
      .replaceAll(" day ahead", " Day Ahead")
      .replace(/\btemp\b/, "Temperature")
      .replace(/\bhumidity\b/, "Humidity")
      .replace(/\bpressure\b/, "Pressure")
      .replace(/\bwind speed\b/, "Wind Speed")
      .replace(/\bhour\b/, "Hour")
      .replace(/\bday\b/, "Day")
      .replace(/\bmonth\b/, "Month")
      .replace(/\bweekday\b/, "Weekday")
      .replace(/\bis weekend\b/, "Is Weekend");
  };

  // ==============================
  // Sort SHAP Features
  // ==============================

  const getSortedExplanation = () => {
    if (!explanation) {
      return [];
    }

    return Object.entries(explanation)
      .map(([feature, value]) => ({
        feature,
        value: Number(value),
      }))
      .sort((a, b) => Math.abs(b.value) - Math.abs(a.value));
  };

  // ==============================
  // SHAP Feature Explanation
  // ==============================

  const renderExplanation = () => {
    if (!explanation) {
      return null;
    }

    const sortedFeatures = getSortedExplanation();

    return (
      <div className="shap-section">
        <h3>🔍 Prediction Explanation</h3>

        <p className="shap-description">
          SHAP values show how each feature contributed to the predicted
          electricity demand. Positive values increase the prediction,
          while negative values decrease it.
        </p>

        <div className="shap-list">
          {sortedFeatures.map((item) => {
            const isPositive = item.value >= 0;

            return (
              <div
                className="shap-row"
                key={item.feature}
              >
                <div className="shap-feature">
                  <span>
                    {formatFeatureName(item.feature)}
                  </span>
                </div>

                <div
                  className={
                    isPositive
                      ? "shap-value positive"
                      : "shap-value negative"
                  }
                >
                  {isPositive ? "+" : ""}
                  {item.value.toFixed(4)}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  // ==============================
  // Main UI
  // ==============================

  return (
    <div className="app">

      {/* ================= HEADER ================= */}

      <header className="header">
        <div>
          <h1>⚡ PowerPredict AI</h1>

          <p>
            Intelligent Energy Demand Forecasting
          </p>
        </div>

        <div className="status">
          <span></span>
          API Connected
        </div>
      </header>

      {/* ================= HERO ================= */}

      <section className="hero">
        <h2>
          Electricity Demand Prediction
        </h2>

        <p>
          Enter weather, renewable energy and
          time-related conditions to predict
          electricity demand using our XGBoost
          model.
        </p>
      </section>

      {/* ================= PREDICTION DASHBOARD ================= */}

      <section className="dashboard">

        {/* ================= INPUT CARD ================= */}

        <div className="card">

          <h3>
            Prediction Inputs
          </h3>

          <form onSubmit={handlePredict}>

            <div className="grid">

              {/* Solar Generation */}

              <div className="input-group">
                <label>
                  Solar Generation
                </label>

                <input
                  type="number"
                  step="any"
                  name="generation_solar"
                  value={formData.generation_solar}
                  onChange={handleChange}
                  placeholder="Enter value"
                  required
                />
              </div>

              {/* Wind Generation */}

              <div className="input-group">
                <label>
                  Wind Generation
                </label>

                <input
                  type="number"
                  step="any"
                  name="generation_wind_onshore"
                  value={formData.generation_wind_onshore}
                  onChange={handleChange}
                  placeholder="Enter value"
                  required
                />
              </div>

              {/* Solar Forecast */}

              <div className="input-group">
                <label>
                  Solar Forecast Day Ahead
                </label>

                <input
                  type="number"
                  step="any"
                  name="forecast_solar_day_ahead"
                  value={formData.forecast_solar_day_ahead}
                  onChange={handleChange}
                  placeholder="Enter value"
                  required
                />
              </div>

              {/* Wind Forecast */}

              <div className="input-group">
                <label>
                  Wind Forecast Day Ahead
                </label>

                <input
                  type="number"
                  step="any"
                  name="forecast_wind_onshore_day_ahead"
                  value={formData.forecast_wind_onshore_day_ahead}
                  onChange={handleChange}
                  placeholder="Enter value"
                  required
                />
              </div>

              {/* Temperature */}

              <div className="input-group">
                <label>
                  Temperature
                </label>

                <input
                  type="number"
                  step="any"
                  name="temp"
                  value={formData.temp}
                  onChange={handleChange}
                  placeholder="Enter temperature"
                  required
                />
              </div>

              {/* Humidity */}

              <div className="input-group">
                <label>
                  Humidity
                </label>

                <input
                  type="number"
                  step="any"
                  name="humidity"
                  value={formData.humidity}
                  onChange={handleChange}
                  placeholder="Enter humidity"
                  required
                />
              </div>

              {/* Pressure */}

              <div className="input-group">
                <label>
                  Pressure
                </label>

                <input
                  type="number"
                  step="any"
                  name="pressure"
                  value={formData.pressure}
                  onChange={handleChange}
                  placeholder="Enter pressure"
                  required
                />
              </div>

              {/* Wind Speed */}

              <div className="input-group">
                <label>
                  Wind Speed
                </label>

                <input
                  type="number"
                  step="any"
                  name="wind_speed"
                  value={formData.wind_speed}
                  onChange={handleChange}
                  placeholder="Enter wind speed"
                  required
                />
              </div>

              {/* Hour */}

              <div className="input-group">
                <label>
                  Hour
                </label>

                <input
                  type="number"
                  min="0"
                  max="23"
                  name="hour"
                  value={formData.hour}
                  onChange={handleChange}
                  placeholder="0 - 23"
                  required
                />
              </div>

              {/* Day */}

              <div className="input-group">
                <label>
                  Day
                </label>

                <input
                  type="number"
                  min="1"
                  max="31"
                  name="day"
                  value={formData.day}
                  onChange={handleChange}
                  placeholder="1 - 31"
                  required
                />
              </div>

              {/* Month */}

              <div className="input-group">
                <label>
                  Month
                </label>

                <input
                  type="number"
                  min="1"
                  max="12"
                  name="month"
                  value={formData.month}
                  onChange={handleChange}
                  placeholder="1 - 12"
                  required
                />
              </div>

              {/* Weekday */}

              <div className="input-group">
                <label>
                  Weekday
                </label>

                <input
                  type="number"
                  min="0"
                  max="6"
                  name="weekday"
                  value={formData.weekday}
                  onChange={handleChange}
                  placeholder="0 - 6"
                  required
                />
              </div>

              {/* Weekend */}

              <div className="input-group">
                <label>
                  Is Weekend
                </label>

                <select
                  name="is_weekend"
                  value={formData.is_weekend}
                  onChange={handleChange}
                  required
                >
                  <option value="">
                    Select
                  </option>

                  <option value="0">
                    No
                  </option>

                  <option value="1">
                    Yes
                  </option>
                </select>
              </div>

            </div>

            {/* Predict Button */}

            <button
              type="submit"
              disabled={loading}
            >
              {loading
                ? "Predicting..."
                : "⚡ Predict Demand"}
            </button>

          </form>

        </div>

        {/* ================= RESULT CARD ================= */}

        <div className="card result-card">

          <h3>
            Prediction Result
          </h3>

          {/* Empty Result */}

          {!prediction && !error && (
            <div className="empty-result">

              <div className="icon">
                ⚡
              </div>

              <p>
                Enter the values and click
                Predict Demand.
              </p>

            </div>
          )}

          {/* Prediction */}

          {prediction !== null && (
            <div className="result">

              <p>
                Predicted Electricity Demand
              </p>

              <h2>
                {Number(prediction).toFixed(2)}
              </h2>

              <span>
                MW
              </span>

            </div>
          )}

          {/* Error */}

          {error && (
            <div className="error">

              <strong>
                Prediction Error
              </strong>

              <p>
                {error}
              </p>

            </div>
          )}

        </div>

      </section>

      {/* ================= SHAP EXPLANATION ================= */}

      {prediction !== null && explanation && (
        <section className="monitoring-section">

          <div className="card monitoring-card">

            {renderExplanation()}

          </div>

        </section>
      )}

      {/* ================= MODEL MONITORING ================= */}

      <section className="monitoring-section">

        <div className="card monitoring-card">

          <h3>
            📊 Model Monitoring
          </h3>

          {monitoring ? (

            <div className="monitoring-grid">

              <div className="metric">
                <span>
                  Model
                </span>

                <strong>
                  {monitoring.model}
                </strong>
              </div>

              <div className="metric">
                <span>
                  Status
                </span>

                <strong className="healthy">
                  🟢 {monitoring.status}
                </strong>
              </div>

              <div className="metric">
                <span>
                  MAE
                </span>

                <strong>
                  {monitoring.mae}
                </strong>
              </div>

              <div className="metric">
                <span>
                  RMSE
                </span>

                <strong>
                  {monitoring.rmse}
                </strong>
              </div>

              <div className="metric">
                <span>
                  R² Score
                </span>

                <strong>
                  {monitoring.r2}
                </strong>
              </div>

            </div>

          ) : (

            <p>
              Loading monitoring data...
            </p>

          )}

        </div>

      </section>

      {/* ================= DATA DRIFT ================= */}

      <section className="monitoring-section">

        <div className="card monitoring-card">

          <h3>
            📈 Data Drift Monitoring
          </h3>

          {!driftData ? (

            <p>
              Loading drift information...
            </p>

          ) : (

            <>

              {/* Drift Summary */}

              <div className="monitoring-grid">

                <div className="metric">

                  <span>
                    Overall Status
                  </span>

                  <strong>
                    {driftData.status === "Healthy"
                      ? "🟢 Healthy"
                      : driftData.status ===
                        "Moderate Drift"
                      ? "🟡 Moderate Drift"
                      : "🔴 Drift Detected"}
                  </strong>

                </div>

                <div className="metric">

                  <span>
                    Significant Drift
                  </span>

                  <strong>
                    {driftData.significant_features}
                  </strong>

                </div>

                <div className="metric">

                  <span>
                    Moderate Drift
                  </span>

                  <strong>
                    {driftData.moderate_features}
                  </strong>

                </div>

              </div>

              {/* Feature Drift */}

              <div className="drift-results">

                <h4>
                  Feature Drift
                </h4>

                {driftData.features &&
                  driftData.features.map((item) => (

                    <div
                      className="drift-row"
                      key={item.feature}
                    >

                      <span>
                        {item.feature}
                      </span>

                      <span>
                        PSI: {item.psi}
                      </span>

                      <strong>

                        {item.status === "No Drift"
                          ? "🟢 No Drift"
                          : item.status ===
                            "Moderate Drift"
                          ? "🟡 Moderate Drift"
                          : "🔴 Significant Drift"}

                      </strong>

                    </div>

                  ))}

              </div>

            </>

          )}

        </div>

      </section>

      {/* ================= FOOTER ================= */}

      <footer>
        <p>
          PowerPredict AI • Intelligent Energy
          Demand Forecasting
        </p>
      </footer>

    </div>
  );
}

export default App;