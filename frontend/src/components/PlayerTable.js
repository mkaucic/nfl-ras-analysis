import React, { useState } from "react";

const PlayerTable = ({ players }) => {
  const [sortField, setSortField] = useState("RAS_numeric");
  const [sortDirection, setSortDirection] = useState("desc");
  const [currentPage, setCurrentPage] = useState(1);
  const playersPerPage = 20;

  const handleSort = (field) => {
    if (field === sortField) {
      setSortDirection(sortDirection === "asc" ? "desc" : "asc");
    } else {
      setSortField(field);
      setSortDirection("desc");
    }
  };

  const sortedPlayers = [...players].sort((a, b) => {
    if (a[sortField] < b[sortField]) return sortDirection === "asc" ? -1 : 1;
    if (a[sortField] > b[sortField]) return sortDirection === "asc" ? 1 : -1;
    return 0;
  });

  // Pagination
  const indexOfLastPlayer = currentPage * playersPerPage;
  const indexOfFirstPlayer = indexOfLastPlayer - playersPerPage;
  const currentPlayers = sortedPlayers.slice(
    indexOfFirstPlayer,
    indexOfLastPlayer,
  );
  const totalPages = Math.ceil(players.length / playersPerPage);

  const getRASColor = (ras) => {
    // If RAS is not a valid number, return gray
    if (!ras || isNaN(ras)) return "#cccccc";

    // Map RAS (0-10) to a color gradient (red to green)
    // For a pastel look, we'll use lighter colors
    if (ras >= 9) return "#c6f6d5"; // Light green for excellent
    if (ras >= 8) return "#d4edd4"; // Pale green for very good
    if (ras >= 7) return "#e2f5d3"; // Light yellowish green for good
    if (ras >= 6) return "#f0fad2"; // Very light yellow-green for above average
    if (ras >= 5) return "#fafad2"; // Light yellow for average
    if (ras >= 4) return "#faecd2"; // Light orange-yellow for below average
    if (ras >= 3) return "#faded2"; // Light orange for poor
    if (ras >= 2) return "#fad0d2"; // Light salmon for very poor
    return "#fac2c2"; // Light red for terrible
  };

  return (
    <div>
      <div className="overflow-x-auto">
        <table className="min-w-full bg-white">
          <thead className="bg-gray-800 text-white">
            <tr>
              <th
                className="py-2 px-4 cursor-pointer"
                onClick={() => handleSort("Player")}
              >
                Player{" "}
                {sortField === "Player" &&
                  (sortDirection === "asc" ? "↑" : "↓")}
              </th>
              <th
                className="py-2 px-4 cursor-pointer"
                onClick={() => handleSort("Position")}
              >
                Position{" "}
                {sortField === "Position" &&
                  (sortDirection === "asc" ? "↑" : "↓")}
              </th>
              <th
                className="py-2 px-4 cursor-pointer"
                onClick={() => handleSort("RAS_numeric")}
              >
                RAS{" "}
                {sortField === "RAS_numeric" &&
                  (sortDirection === "asc" ? "↑" : "↓")}
              </th>
              <th
                className="py-2 px-4 cursor-pointer"
                onClick={() => handleSort("Pro_Bowls_numeric")}
              >
                Pro Bowls{" "}
                {sortField === "Pro_Bowls_numeric" &&
                  (sortDirection === "asc" ? "↑" : "↓")}
              </th>
              <th
                className="py-2 px-4 cursor-pointer"
                onClick={() => handleSort("College")}
              >
                College{" "}
                {sortField === "College" &&
                  (sortDirection === "asc" ? "↑" : "↓")}
              </th>
              <th
                className="py-2 px-4 cursor-pointer"
                onClick={() => handleSort("Draft")}
              >
                Draft Year{" "}
                {sortField === "Draft" && (sortDirection === "asc" ? "↑" : "↓")}
              </th>
            </tr>
          </thead>
          <tbody className="text-gray-700">
            {currentPlayers.map((player, index) => (
              <tr
                key={index}
                className={index % 2 === 0 ? "bg-gray-100" : "bg-white"}
              >
                <td className="py-2 px-4">
                  {player.Profile_URL ? (
                    <a
                      href={player.Profile_URL}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:underline"
                    >
                      {player.Player}
                    </a>
                  ) : (
                    // If we don't have a Profile_URL, create a reasonable guess at the URL
                    <a
                      href={`https://ras.football/search/${player.Player.toLowerCase().replace(
                        /\s+/g,
                        "-",
                      )}/`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:underline"
                    >
                      {player.Player}
                    </a>
                  )}
                </td>
                <td className="py-2 px-4">{player.Position}</td>
                <td
                  className="py-2 px-4"
                  style={{
                    backgroundColor: getRASColor(player.RAS_numeric),
                    fontWeight: "medium",
                  }}
                >
                  {player.RAS_numeric ? player.RAS_numeric.toFixed(2) : "N/A"}
                </td>
                <td className="py-2 px-4">{player.Pro_Bowls_numeric}</td>
                <td className="py-2 px-4">{player.College}</td>
                <td className="py-2 px-4">{player.Draft}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="flex justify-between items-center mt-4">
        <div>
          Showing {indexOfFirstPlayer + 1}-
          {Math.min(indexOfLastPlayer, players.length)} of {players.length}{" "}
          players
        </div>
        <div className="flex space-x-2">
          <button
            onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
            disabled={currentPage === 1}
            className="px-3 py-1 bg-gray-200 rounded disabled:opacity-50"
          >
            Previous
          </button>
          <span className="px-3 py-1">
            Page {currentPage} of {totalPages}
          </span>
          <button
            onClick={() =>
              setCurrentPage(Math.min(totalPages, currentPage + 1))
            }
            disabled={currentPage === totalPages}
            className="px-3 py-1 bg-gray-200 rounded disabled:opacity-50"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
};

export default PlayerTable;
