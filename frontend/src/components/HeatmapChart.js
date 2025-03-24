import React from "react";

const HeatmapChart = ({ data }) => {
  // Check if data exists and has the right format
  if (!data || typeof data !== "object" || Object.keys(data).length === 0) {
    return <div className="p-4 text-center">No correlation data available</div>;
  }

  // Get keys (measures) from the data
  const measures = Object.keys(data);

  // Function to determine cell color based on correlation value
  const getCellColor = (value) => {
    // Define color scale from blue (negative) to white (neutral) to red (positive)
    if (value === null || value === undefined) return "#f0f0f0";

    if (value > 0) {
      // Positive correlation: white to red
      const intensity = Math.min(Math.round(value * 255), 255);
      return `rgb(255, ${255 - intensity}, ${255 - intensity})`;
    } else {
      // Negative correlation: white to blue
      const intensity = Math.min(Math.round(Math.abs(value) * 255), 255);
      return `rgb(${255 - intensity}, ${255 - intensity}, 255)`;
    }
  };

  return (
    <div className="overflow-auto">
      <table className="border-collapse w-full">
        <thead>
          <tr>
            <th className="border p-2 bg-gray-100"></th>
            {measures.map((measure) => (
              <th
                key={measure}
                className="border p-2 bg-gray-100 text-sm font-medium"
              >
                {measure}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {measures.map((row) => (
            <tr key={row}>
              <th className="border p-2 bg-gray-100 text-sm font-medium text-left">
                {row}
              </th>
              {measures.map((col) => {
                // Get correlation value, defaulting to 0 if not found
                const value =
                  data[row] && typeof data[row] === "object"
                    ? data[row][col] || 0
                    : 0;
                return (
                  <td
                    key={`${row}-${col}`}
                    className="border p-2 text-center"
                    style={{
                      backgroundColor: getCellColor(value),
                      color: Math.abs(value) > 0.5 ? "white" : "black",
                    }}
                  >
                    {typeof value === "number" ? value.toFixed(2) : "N/A"}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default HeatmapChart;
