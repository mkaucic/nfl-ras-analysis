import React, { useState } from "react";
import { Link } from "react-router-dom";

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
    indexOfLastPlayer
  );
  const totalPages = Math.ceil(players.length / playersPerPage);

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
                  <a
                    href={player.Profile_URL}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline"
                  >
                    {player.Player}
                  </a>
                </td>
                <td className="py-2 px-4">{player.Position}</td>
                <td className="py-2 px-4">
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
