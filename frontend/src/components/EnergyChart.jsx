
// Import React hooks for storing, loading, and updating the chart data.
import { useEffect, useState } from "react";

// Import the required chart components from Recharts.
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    Tooltip,
    CartesianGrid
} from "recharts";

// Create the EnergyChart component and receive the latest prediction from App.jsx.
function EnergyChart({ newPrediction }) {

    // Create state to store the historical and prediction data for the chart.
    const [data, setData] = useState([]);

    // Create state to track whether the historical data is still loading.
    const [loading, setLoading] = useState(true);

    // Create state to store any API error.
    const [error, setError] = useState(null);

    // Run this code once when the EnergyChart component is loaded.
    useEffect(() => {

        // Request the latest energy-demand data from the Flask API.
        fetch("http://127.0.0.1:5000/energy-trend")

            // Convert the API response into JSON.
            .then((response) => {

                // Check whether the API request was successful.
                if (!response.ok) {

                    // Stop the request if the API returned an error.
                    throw new Error("Failed to load energy trend data");

                }

                // Return the JSON response.
                return response.json();

            })

            // Process the JSON data returned by Flask.
            .then((result) => {

                // Convert the API records into the format required by Recharts.
                const chartData = result.map((item) => ({

                    // Use the actual historical timestamp as the X-axis value.
                    time: item.time,

                    // Use the actual historical electricity demand as the Y-axis value.
                    demand: item.demand

                }));

                // Store the historical chart data in React state.
                setData(chartData);

                // Stop displaying the loading message.
                setLoading(false);

            })

            // Handle any API or network error.
            .catch((err) => {

                // Display the error in the browser console.
                console.error("Energy Trend Error:", err);

                // Store the error message.
                setError(err.message);

                // Stop displaying the loading message.
                setLoading(false);

            });

    // Empty dependency array means this API request runs once.
    }, []);

    // Add a new prediction to the chart whenever App.jsx sends a new prediction.
    useEffect(() => {

        // Check whether a new prediction is available.
        if (newPrediction) {

            // Add the new prediction to the existing chart data.
            setData((previousData) => [

                // Keep all existing historical and prediction data.
                ...previousData,

                // Add the new prediction as the newest chart point.
                {
                    // Use the current timestamp received from App.jsx.
                    time: newPrediction.time,

                    // Use the predicted electricity demand value.
                    demand: newPrediction.demand

                }

            ]);

        }

    // Run this effect whenever the prediction changes.
    }, [newPrediction]);

    // Display a loading message while the historical data is being fetched.
    if (loading) {

        // Return the loading message.
        return (
            <div className="bg-gray-900 p-6 rounded-xl">

                {/* Display the chart title. */}
                <h2 className="text-2xl text-cyan-400 mb-5">
                    Energy Demand Trend
                </h2>

                {/* Display the loading status. */}
                <p className="text-gray-300">
                    Loading energy demand data...
                </p>

            </div>
        );

    }

    // Display an error message if the historical API request failed.
    if (error) {

        // Return the error section.
        return (
            <div className="bg-gray-900 p-6 rounded-xl">

                {/* Display the chart title. */}
                <h2 className="text-2xl text-cyan-400 mb-5">
                    Energy Demand Trend
                </h2>

                {/* Display the error message. */}
                <p className="text-red-400">
                    Unable to load energy trend data.
                </p>

            </div>
        );

    }

    // Display the actual energy-demand chart.
    return (

        // Create the chart container.
        <div className="bg-gray-900 p-6 rounded-xl">

            {/* Display the chart title. */}
            <h2 className="text-2xl text-cyan-400 mb-2">
                Energy Demand Trend
            </h2>

            {/* Explain that the chart contains historical data and new predictions. */}
            <p className="text-gray-400 mb-5">
                Historical electricity demand with newly generated predictions.
            </p>

            {/* Create the Recharts line chart. */}
            <LineChart
                width={500}
                height={300}
                data={data}
            >

                {/* Display the background grid. */}
                <CartesianGrid strokeDasharray="3 3" />

                {/* Display date and time on the X-axis. */}
                <XAxis
                    dataKey="time"
                    stroke="#9CA3AF"
                    tickFormatter={(value) => {

                        // Convert the timestamp into a JavaScript Date object.
                        const date = new Date(value);

                        // Format the date and time for display.
                        return date.toLocaleString("en-IN", {
                            month: "short",
                            day: "numeric",
                            hour: "2-digit",
                            minute: "2-digit"
                        });

                    }}
                />

                {/* Display electricity demand on the Y-axis. */}
                <YAxis
                    stroke="#9CA3AF"
                />

                {/* Display demand and timestamp when the user hovers over a point. */}
                <Tooltip />

                {/* Draw the electricity-demand line. */}
                <Line
                    type="monotone"
                    dataKey="demand"
                    stroke="#22D3EE"
                    strokeWidth={3}
                    dot={false}
                />

            </LineChart>

        </div>

    );

}

// Export the EnergyChart component so App.jsx can use it.
export default EnergyChart;
