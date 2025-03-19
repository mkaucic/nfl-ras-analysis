import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { BarChart, Bar } from "recharts";
import PlayerTable from "../components/PlayerTable";

const Dashboard = () => {
  const [playersData, setPlayersData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [positionFilter, setPositionFilter] = useState("All");
  const [positions, setPositions] = useState([]);
  const [positionStats, setPositionStats] = useState([]);

  useEffect(() => {
    // Load the processed data
    setLoading(true);
    fetch("/data/processed_data.json")
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
      })
      .then((data) => {
        console.log("Data loaded successfully:", data.length, "records");
        setPlayersData(data);

        // Extract unique positions
        const uniquePositions = [
          ...new Set(data.map((player) => player.Position)),
        ];
        setPositions(["All", ...uniquePositions]);

        // Calculate position stats
        const stats = uniquePositions.map((position) => {
          const posPlayers = data.filter((p) => p.Position === position);
          const avgRAS =
            posPlayers.reduce((sum, p) => sum + (p.RAS_numeric || 0), 0) /
            posPlayers.length;
          const totalProBowls = posPlayers.reduce(
            (sum, p) => sum + (p.Pro_Bowls_numeric || 0),
            0
          );

          return {
            position,
            avgRAS: avgRAS.toFixed(2),
            playerCount: posPlayers.length,
            totalProBowls,
          };
        });

        setPositionStats(stats);
        setLoading(false);
      })
      .catch((error) => {
        console.error("Error loading data:", error);
        setLoading(false);
        // Show user-friendly error message
        alert(
          "Failed to load player data. Please check the console for details."
        );
      });
  }, []);

  const filteredPlayers =
    positionFilter === "All"
      ? playersData
      : playersData.filter((player) => player.Position === positionFilter);

  if (loading) {
    return <div className="text-center py-10">Loading data...</div>;
  }

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">
        The Importance of RAS in NFL Pro Bowl Selection
      </h1>

      <div className="mb-6">
        <h2 className="text-xl font-semibold mb-2">Position Filter</h2>
        <div className="flex flex-wrap gap-2">
          {positions.map((pos) => (
            <button
              key={pos}
              className={`px-3 py-1 rounded ${
                positionFilter === pos
                  ? "bg-blue-600 text-white"
                  : "bg-gray-200"
              }`}
              onClick={() => setPositionFilter(pos)}
            >
              {pos}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div className="bg-white p-4 rounded shadow">
          <h2 className="text-xl font-semibold mb-4">
            RAS vs Pro Bowl Appearances
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
              <CartesianGrid />
              <XAxis
                type="number"
                dataKey="RAS_numeric"
                name="RAS"
                domain={[0, 10]}
              />
              <YAxis
                type="number"
                dataKey="Pro_Bowls_numeric"
                name="Pro Bowls"
              />
              <Tooltip
                cursor={{ strokeDasharray: "3 3" }}
                formatter={(value, name) => [value, name]}
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const player = payload[0].payload;
                    return (
                      <div className="bg-white p-3 border rounded shadow-md">
                        <p className="font-bold">{player.Player}</p>
                        <p>Position: {player.Position}</p>
                        <p>RAS: {player.RAS_numeric?.toFixed(2) || "N/A"}</p>
                        <p>Pro Bowls: {player.Pro_Bowls_numeric || "N/A"}</p>
                        <p>College: {player.College || "N/A"}</p>
                        <p>Draft: {player.Draft || "N/A"}</p>
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Legend />
              <Scatter
                name="Players"
                data={filteredPlayers}
                fill="#8884d8"
                shape="circle"
              />
            </ScatterChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white p-4 rounded shadow">
          <h2 className="text-xl font-semibold mb-4">
            Average RAS by Position
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart
              data={positionStats}
              margin={{ top: 20, right: 30, left: 20, bottom: 60 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="position" angle={-45} textAnchor="end" />
              <YAxis domain={[0, 10]} />
              <Tooltip />
              <Legend />
              <Bar dataKey="avgRAS" fill="#82ca9d" name="Avg RAS" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="bg-white p-4 rounded shadow mb-8">
        <h2 className="text-xl font-semibold mb-4">Pro Bowlers Data</h2>
        <PlayerTable players={filteredPlayers} />
      </div>
    </div>
  );
};

export default Dashboard;
