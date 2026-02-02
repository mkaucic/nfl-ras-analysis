import React, { useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const PositionInsights = ({ positionData }) => {
  const [selectedPosition, setSelectedPosition] = useState(null);

  // Sort positions by player count (most common first)
  const sortedPositions = [...positionData].sort(
    (a, b) => b.PlayerCount - a.PlayerCount,
  );

  return (
    <div>
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2 mb-6">
        {sortedPositions.map((position) => (
          <button
            key={position.Position}
            className={`px-3 py-2 rounded text-sm ${
              selectedPosition?.Position === position.Position
                ? "bg-blue-600 text-white"
                : "bg-gray-200"
            }`}
            onClick={() => setSelectedPosition(position)}
          >
            {position.Position} ({position.PlayerCount})
          </button>
        ))}
      </div>

      {!selectedPosition ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <div className="bg-white p-4 rounded shadow">
            <h3 className="text-lg font-semibold mb-4">
              Average RAS by Position
            </h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart
                data={sortedPositions.sort((a, b) => b.AvgRAS - a.AvgRAS)}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="Position" />
                <YAxis domain={[0, 10]} />
                <Tooltip formatter={(value) => value.toFixed(2)} />
                <Bar dataKey="AvgRAS" fill="#8884d8" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-white p-4 rounded shadow">
            <h3 className="text-lg font-semibold mb-4">
              Multiple Pro Bowl Rate by Position
            </h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart
                data={sortedPositions.sort(
                  (a, b) => b.MultiProBowlRate - a.MultiProBowlRate,
                )}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="Position" />
                <YAxis domain={[0, 100]} />
                <Tooltip formatter={(value) => `${value.toFixed(1)}%`} />
                <Bar dataKey="MultiProBowlRate" fill="#82ca9d" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      ) : (
        <div className="bg-white p-6 rounded shadow">
          <h3 className="text-xl font-semibold mb-4">
            {selectedPosition.Position} Position Insights
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="bg-gray-100 p-4 rounded">
              <p className="text-sm text-gray-600">Average RAS</p>
              <p className="text-2xl font-bold">
                {selectedPosition.AvgRAS.toFixed(2)}
              </p>
            </div>
            <div className="bg-gray-100 p-4 rounded">
              <p className="text-sm text-gray-600">Average Pro Bowls</p>
              <p className="text-2xl font-bold">
                {selectedPosition.AvgProBowls.toFixed(2)}
              </p>
            </div>
            <div className="bg-gray-100 p-4 rounded">
              <p className="text-sm text-gray-600">Multiple Pro Bowl Rate</p>
              <p className="text-2xl font-bold">
                {selectedPosition.MultiProBowlRate.toFixed(1)}%
              </p>
            </div>
          </div>

          <p className="mb-6">
            {selectedPosition.Position} players with high RAS scores are
            {selectedPosition.AvgRAS > 7
              ? " significantly"
              : selectedPosition.AvgRAS > 5
                ? " moderately"
                : " slightly"}
            more likely to make multiple Pro Bowls, with an average RAS of{" "}
            {selectedPosition.AvgRAS.toFixed(2)}
            among Pro Bowlers.
          </p>

          <div className="mt-4">
            <p className="text-sm text-gray-500 italic">
              Note: Position-specific RAS distribution and scatter plot images
              would be displayed here when available.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default PositionInsights;
