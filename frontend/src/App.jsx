// Import React hooks used for state management and side effects.
import { useEffect, useState } from "react";

// Import the Energy Demand Trend chart component.
import EnergyChart from "./components/EnergyChart";

// Import the CSS file for this application.
import "./App.css";

// Main App component.
function App() {
  // ==============================
  // Form Data
  // ==============================

  // Store all prediction input values entered by the user.
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

  // Store the latest predicted electricity demand.
  const [prediction, setPrediction] = useState(null);

  // Store SHAP explanation returned by the backend.
  const [explanation, setExplanation] = useState(null);

  // Store prediction loading state.
  const [loading, setLoading] = useState(false);

  // Store prediction error message.
  const [error, setError] = useState("");

  // Store the latest prediction for the Energy Trend chart.
  const [newPrediction, setNewPrediction] = useState(null);

  // ==============================
  // Monitoring State
  // ==============================

  // Store model monitoring information.
  const [monitoring, setMonitoring] = useState(null);

  // Store data drift information.
  const [driftData, setDriftData] = useState(null);

  // ==============================
  // Renewable Energy State
  // ==============================

  // Store renewable energy information.
  const [renewableData, setRenewableData] = useState(null);

  // ==============================
  // Model Monitoring
  // ==============================

  // Load model monitoring information when the application starts.
  useEffect(() => {
    // Call the Flask monitoring endpoint.
    fetch("http://127.0.0.1:5000/monitoring")
      // Check whether the response was successful.
      .then((response) => {
        // Throw an error when the response is unsuccessful.
        if (!response.ok) {
          throw new Error("Failed to load monitoring data");
        }

        // Convert the response into JSON.
        return response.json();
      })

      // Store the monitoring data in React state.
      .then((data) => {
        setMonitoring(data);
      })

      // Handle monitoring errors.
      .catch((err) => {
        console.error("Monitoring error:", err);
      });
  }, []);

  // ==============================
  // Data Drift Monitoring
  // ==============================

  // Recalculate drift whenever the user changes an input value.
  useEffect(() => {
    // Do not call the backend when form data is unavailable.
    if (!formData) {
      return;
    }

    // Convert frontend field names into backend feature names.
    const driftInput = {
      "generation solar": Number(formData.generation_solar) || 0,
      "generation wind onshore":
        Number(formData.generation_wind_onshore) || 0,
      "forecast solar day ahead":
        Number(formData.forecast_solar_day_ahead) || 0,
      "forecast wind onshore day ahead":
        Number(formData.forecast_wind_onshore_day_ahead) || 0,
      temp: Number(formData.temp) || 0,
      humidity: Number(formData.humidity) || 0,
      pressure: Number(formData.pressure) || 0,
      wind_speed: Number(formData.wind_speed) || 0,
      hour: Number(formData.hour) || 0,
      day: Number(formData.day) || 0,
      month: Number(formData.month) || 0,
      weekday: Number(formData.weekday) || 0,
      is_weekend: Number(formData.is_weekend) || 0,
    };

    // Send the current input values to the Flask drift endpoint.
    fetch("http://127.0.0.1:5000/drift", {
      // Use POST because the backend expects current input data.
      method: "POST",

      // Tell Flask that the request body contains JSON.
      headers: {
        "Content-Type": "application/json",
      },

      // Convert the JavaScript object into JSON.
      body: JSON.stringify(driftInput),
    })
      // Convert the response into JSON.
      .then((response) => {
        // Throw an error when the request fails.
        if (!response.ok) {
          throw new Error("Failed to load drift data");
        }

        // Return the JSON response.
        return response.json();
      })

      // Store the drift information.
      .then((data) => {
        setDriftData(data);
      })

      // Handle drift errors.
      .catch((error) => {
        console.error("Data Drift Error:", error);
      });
  }, [formData]);

  // ==============================
  // Renewable Energy Monitoring
  // ==============================

  // Recalculate renewable energy information whenever inputs change.
  useEffect(() => {
    // Do not call the backend when form data is unavailable.
    if (!formData) {
      return;
    }

    // Convert frontend field names into backend feature names.
    const renewableInput = {
      "generation solar": Number(formData.generation_solar) || 0,
      "generation wind onshore":
        Number(formData.generation_wind_onshore) || 0,
      "generation wind offshore": 0,
      "forecast solar day ahead":
        Number(formData.forecast_solar_day_ahead) || 0,
      "forecast wind onshore day ahead":
        Number(formData.forecast_wind_onshore_day_ahead) || 0,
      temp: Number(formData.temp) || 0,
      humidity: Number(formData.humidity) || 0,
      pressure: Number(formData.pressure) || 0,
      wind_speed: Number(formData.wind_speed) || 0,
      hour: Number(formData.hour) || 0,
      day: Number(formData.day) || 0,
      month: Number(formData.month) || 0,
      weekday: Number(formData.weekday) || 0,
      is_weekend: Number(formData.is_weekend) || 0,
    };

    // Send the current input values to the renewable endpoint.
    fetch("http://127.0.0.1:5000/renewable", {
      // Use POST because the backend expects current input data.
      method: "POST",

      // Tell Flask that the request body contains JSON.
      headers: {
        "Content-Type": "application/json",
      },

      // Convert the object into JSON.
      body: JSON.stringify(renewableInput),
    })
      // Convert the response into JSON.
      .then((response) => {
        // Throw an error when the request fails.
        if (!response.ok) {
          throw new Error("Failed to load renewable energy data");
        }

        // Return the JSON response.
        return response.json();
      })

      // Store renewable energy information.
      .then((data) => {
        setRenewableData(data);
      })

      // Handle renewable energy errors.
      .catch((error) => {
        console.error("Renewable Energy Error:", error);
      });
  }, [formData]);

  // ==============================
  // Handle Input Changes
  // ==============================

  // Handle changes made to any input field.
  const handleChange = (e) => {
    // Get the input field name and current value.
    const { name, value } = e.target;

    // Update only the changed field while keeping other fields unchanged.
    setFormData((previousData) => ({
      ...previousData,
      [name]: value,
    }));
  };

  // ==============================
  // Prediction
  // ==============================

  // Handle the prediction form submission.
  const handlePredict = async (e) => {
    // Prevent the browser from refreshing the page.
    e.preventDefault();

    // Show the prediction loading state.
    setLoading(true);

    // Clear the previous prediction.
    setPrediction(null);

    // Clear the previous SHAP explanation.
    setExplanation(null);

    // Clear any previous error.
    setError("");

    try {
      // Send the prediction request to Flask.
      const response = await fetch(
        "http://127.0.0.1:5000/predict",
        {
          // Use POST because prediction inputs are being submitted.
          method: "POST",

          // Tell Flask that the request body is JSON.
          headers: {
            "Content-Type": "application/json",
          },

          // Convert frontend field names into backend feature names.
          body: JSON.stringify({
            "generation solar":
              Number(formData.generation_solar),

            "generation wind onshore":
              Number(formData.generation_wind_onshore),

            "forecast solar day ahead":
              Number(formData.forecast_solar_day_ahead),

            "forecast wind onshore day ahead":
              Number(formData.forecast_wind_onshore_day_ahead),

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
        }
      );

      // Convert the response into JSON.
      const data = await response.json();

      // Check whether Flask returned an error.
      if (!response.ok) {
        throw new Error(data.error || "Prediction failed");
      }

      // Store the predicted demand.
      setPrediction(data.prediction);

      // Store the SHAP explanation.
      setExplanation(data.explanation || null);

      // Send the new prediction to the Energy Trend chart.
      setNewPrediction({
        // Store the current timestamp.
        time: new Date().toISOString(),

        // Store the prediction as a number.
        demand: Number(data.prediction),
      });
    } catch (err) {
      // Print the prediction error in the browser console.
      console.error("Prediction error:", err);

      // Display the error message in the UI.
      setError(err.message);
    } finally {
      // Stop the loading state.
      setLoading(false);
    }
  };

  // ==============================
  // Format Feature Name
  // ==============================

  // Convert backend feature names into readable names.
  const formatFeatureName = (feature) => {
    // Apply multiple formatting rules to the feature name.
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

  // Sort SHAP features according to their absolute contribution.
  const getSortedExplanation = () => {
    // Return an empty array when no explanation exists.
    if (!explanation) {
      return [];
    }

    // Convert the explanation object into an array and sort it.
    return Object.entries(explanation)
      .map(([feature, value]) => ({
        feature,
        value: Number(value),
      }))
      .sort(
        (a, b) =>
          Math.abs(b.value) - Math.abs(a.value)
      );
  };

  // ==============================
  // SHAP Feature Explanation
  // ==============================

  // Render the SHAP explanation section.
  const renderExplanation = () => {
    // Do not render anything when no explanation exists.
    if (!explanation) {
      return null;
    }

    // Get the sorted SHAP features.
    const sortedFeatures = getSortedExplanation();

    // Return the SHAP explanation UI.
    return (
      <div className="shap-section">
        {/* SHAP section title. */}
        <h3 className="section-title">
          🔍 Prediction Explanation
        </h3>

        {/* Explain what SHAP values mean. */}
        <p className="shap-description">
          SHAP values show how each feature contributed to
          the predicted electricity demand. Positive values
          increase the prediction, while negative values
          decrease it.
        </p>

        {/* Display all SHAP features. */}
        <div className="shap-list">
          {sortedFeatures.map((item) => {
            // Determine whether the SHAP value is positive.
            const isPositive = item.value >= 0;

            // Return one SHAP feature row.
            return (
              <div
                className="shap-row"
                key={item.feature}
              >
                {/* Display the readable feature name. */}
                <div className="shap-feature">
                  <span>
                    {formatFeatureName(item.feature)}
                  </span>
                </div>

                {/* Display the SHAP value. */}
                <div
                  className={
                    isPositive
                      ? "shap-value positive"
                      : "shap-value negative"
                  }
                >
                  {/* Add + sign to positive values. */}
                  {isPositive ? "+" : ""}

                  {/* Display the SHAP value with four decimal places. */}
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

  // Return the complete application interface.
  return (
    <div className="app">

      {/* ================= HEADER ================= */}

      <header className="header">
        <div>
          <h1>
            ⚡ PowerPredict AI
          </h1>

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

      {/* ================= OVERVIEW ================= */}

      <section className="overview">

        <div className="overview-card">
          <span className="overview-label">
            Model
          </span>

          <strong>
            XGBoost
          </strong>
        </div>

        <div className="overview-card">
          <span className="overview-label">
            R² Score
          </span>

          <strong>
            0.9928
          </strong>
        </div>

        <div className="overview-card">
          <span className="overview-label">
            MAE
          </span>

          <strong>
            260.95
          </strong>
        </div>

        <div className="overview-card">
          <span className="overview-label">
            RMSE
          </span>

          <strong>
            386.41
          </strong>
        </div>

        <div className="overview-card">
          <span className="overview-label">
            Data Drift
          </span>

          <strong>
            {driftData
              ? driftData.status === "Healthy"
                ? "🟢 Healthy"
                : driftData.status === "Moderate Drift"
                ? "🟡 Moderate"
                : "🔴 Detected"
              : "Loading"}
          </strong>
        </div>

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

          <h3 className="section-title">
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
        <section className="explanation-section">

          <div className="card explanation-card">

            {renderExplanation()}

          </div>

        </section>
      )}

      {/* ================= ENERGY DEMAND TREND ================= */}

      <EnergyChart
        newPrediction={newPrediction}
      />

      {/* ================= MODEL MONITORING ================= */}

      <section className="monitoring-section">

        <div className="card monitoring-card">

          <h3>
            📊 Model Monitoring
          </h3>

          {monitoring ? (

            <div className="monitoring-grid">

              {/* Model */}

              <div className="metric">

                <span>
                  Model
                </span>

                <strong>
                  {monitoring.model}
                </strong>

              </div>

              {/* Status */}

              <div className="metric">

                <span>
                  Status
                </span>

                <strong className="healthy">
                  🟢 {monitoring.status}
                </strong>

              </div>

              {/* MAE */}

              <div className="metric">

                <span>
                  MAE
                </span>

                <strong>
                  {monitoring.mae}
                </strong>

              </div>

              {/* RMSE */}

              <div className="metric">

                <span>
                  RMSE
                </span>

                <strong>
                  {monitoring.rmse}
                </strong>

              </div>

              {/* R² */}

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

                {/* Overall Status */}

                <div className="metric">

                  <span>
                    Overall Status
                  </span>

                  <strong>
                    {driftData.status === "Healthy"
                      ? "🟢 Healthy"
                      : driftData.status === "Moderate Drift"
                      ? "🟡 Moderate Drift"
                      : "🔴 Drift Detected"}
                  </strong>

                </div>

                {/* Significant Drift */}

                <div className="metric">

                  <span>
                    Significant Drift
                  </span>

                  <strong>
                    {driftData.significant_features}
                  </strong>

                </div>

                {/* Moderate Drift */}

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

                      {/* Feature name */}

                      <span>
                        {formatFeatureName(item.feature)}
                      </span>

                      {/* PSI value */}

                      <span>
                        PSI: {item.psi}
                      </span>

                      {/* Drift status */}

                      <strong>
                        {item.status === "No Drift"
                          ? "🟢 No Drift"
                          : item.status === "Moderate Drift"
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

      {/* ================= RENEWABLE ENERGY ================= */}

      <section className="monitoring-section">

        <div className="card monitoring-card">

          <h3>
            🌱 Renewable Energy Overview
          </h3>

          {renewableData ? (

            <div className="monitoring-grid">

              {/* Solar Generation */}

              <div className="metric">

                <span>
                  Solar Generation
                </span>

                <strong>
                  {renewableData.solar_generation} MW
                </strong>

              </div>

              {/* Wind Onshore */}

              <div className="metric">

                <span>
                  Wind Onshore
                </span>

                <strong>
                  {renewableData.wind_onshore_generation} MW
                </strong>

              </div>

              {/* Wind Offshore */}

              <div className="metric">

                <span>
                  Wind Offshore
                </span>

                <strong>
                  {renewableData.wind_offshore_generation} MW
                </strong>

              </div>

              {/* Total Wind */}

              <div className="metric">

                <span>
                  Total Wind
                </span>

                <strong>
                  {renewableData.total_wind_generation} MW
                </strong>

              </div>

              {/* Total Renewable */}

              <div className="metric">

                <span>
                  Total Renewable
                </span>

                <strong>
                  {renewableData.total_renewable_generation} MW
                </strong>

              </div>

              {/* Total Load */}

              <div className="metric">

                <span>
                  Total Load
                </span>

                <strong>
                  {renewableData.total_load} MW
                </strong>

              </div>

              {/* Renewable Share */}

              <div className="metric">

                <span>
                  Renewable Share
                </span>

                <strong>
                  {renewableData.renewable_share}%
                </strong>

              </div>

            </div>

          ) : (

            <p>
              Loading renewable energy data...
            </p>

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

// Export the App component.
export default App;