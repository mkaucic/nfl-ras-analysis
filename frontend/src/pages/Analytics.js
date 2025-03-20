import React, { useState, useEffect } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

const Analytics = () => {
  const [predictions, setPredictions] = useState([]);
  const [positions, setPositions] = useState([]);
  const [selectedPosition, setSelectedPosition] = useState("All");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Load the ML predictions data
    fetch("/data/ml_predictions.json")
      .then((response) => response.json())
      .then((data) => {
        // Sort by RAS for proper line display
        const sortedData = data.sort((a, b) => a.RAS - b.RAS);
        setPredictions(sortedData);
        // Extract unique positions
        const uniquePositions = [...new Set(data.map((p) => p.Position))];
        setPositions(["All", ...uniquePositions.filter((p) => p !== "All")]);

        setLoading(false);
      })
      .catch((error) => {
        console.error("Error loading prediction data:", error);
        setLoading(false);
      });
  }, []);

  // Filter data based on selected position
  const filteredData =
    selectedPosition === "All"
      ? predictions
      : predictions.filter((p) => p.Position === selectedPosition);

  if (loading) {
    return (
      <div className="text-center py-10">
        Loading advanced analytics data...
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Advanced RAS Analytics</h1>

      <div className="bg-white p-6 rounded shadow mb-8">
        <h2 className="text-xl font-semibold mb-4">Statistical Findings</h2>
        <p className="mb-4">
          Our analysis reveals a significant correlation between Relative
          Athletic Score (RAS) and Pro Bowl selections, with higher RAS values
          generally associated with more Pro Bowl appearances.
        </p>
        <p className="mb-4">
          The multiple regression analysis, which controls for position and
          draft round, confirms that RAS remains a significant predictor of NFL
          success even when accounting for these other factors.
        </p>
        <p>
          Machine learning models trained on this data can predict with
          reasonable accuracy the likelihood of a player making multiple Pro
          Bowls based on their RAS score, position, and draft information.
        </p>
      </div>

      <div className="mb-6">
        <h2 className="text-xl font-semibold mb-2">Position Filter</h2>
        <div className="flex flex-wrap gap-2">
          {positions.map((pos) => (
            <button
              key={pos}
              className={`px-3 py-1 rounded ${
                selectedPosition === pos
                  ? "bg-blue-600 text-white"
                  : "bg-gray-200"
              }`}
              onClick={() => setSelectedPosition(pos)}
            >
              {pos}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div className="bg-white p-4 rounded shadow">
          <h2 className="text-xl font-semibold mb-4">
            Pro Bowl Probability by RAS (Logistic Regression)
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={filteredData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="RAS" />
              <YAxis
                domain={[0, 1]}
                tickFormatter={(tick) => `${(tick * 100).toFixed(0)}%`}
                label={{
                  value: "Probability",
                  angle: -90,
                  position: "insideLeft",
                }}
              />
              <Tooltip
                formatter={(value) => [
                  `${(value * 100).toFixed(2)}%`,
                  "Probability",
                ]}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="LogisticRegression_Prob"
                name="Multiple Pro Bowls"
                stroke="#8884d8"
                activeDot={{ r: 8 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white p-4 rounded shadow">
          <h2 className="text-xl font-semibold mb-4">
            Pro Bowl Probability by RAS (Random Forest)
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={filteredData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="RAS" />
              <YAxis
                domain={[0, 1]}
                tickFormatter={(tick) => `${(tick * 100).toFixed(0)}%`}
                label={{
                  value: "Probability",
                  angle: -90,
                  position: "insideLeft",
                }}
              />
              <Tooltip
                formatter={(value) => [
                  `${(value * 100).toFixed(2)}%`,
                  "Probability",
                ]}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="RandomForest_Prob"
                name="Multiple Pro Bowls"
                stroke="#82ca9d"
                activeDot={{ r: 8 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="bg-white p-6 rounded shadow mb-8">
        <h2 className="text-xl font-semibold mb-4">Interpretation</h2>
        <p className="mb-4">
          The charts above show the predicted probability of a player making
          multiple Pro Bowl appearances based on their Relative Athletic Score
          (RAS). Two different machine learning models are displayed:
        </p>
        <ol className="list-decimal list-inside mb-4">
          <li className="mb-2">
            <span className="font-medium">Logistic Regression</span>: A simpler
            model that assumes a linear relationship between RAS and Pro Bowl
            likelihood.
          </li>
          <li>
            <span className="font-medium">Random Forest</span>: A more complex
            model that can capture non-linear relationships and interactions
            between features.
          </li>
        </ol>
        <p className="mb-4">
          As the charts illustrate, players with higher RAS scores generally
          have a higher probability of making multiple Pro Bowls, though this
          relationship varies by position.
        </p>
        <p>
          This analysis supports the importance of athletic testing in NFL draft
          evaluation, while acknowledging that RAS is just one of many factors
          that contribute to a player's success in the league.
        </p>
      </div>
    </div>
  );
};

export default Analytics;
