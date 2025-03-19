import React, { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";

const PlayerDetails = () => {
  const { playerId } = useParams();
  const [player, setPlayer] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Load player data
    fetch("/data/processed_data.json")
      .then((response) => response.json())
      .then((data) => {
        const foundPlayer = data.find((p) => p.Player === playerId);
        setPlayer(foundPlayer || null);
        setLoading(false);
      })
      .catch((error) => {
        console.error("Error loading player data:", error);
        setLoading(false);
      });
  }, [playerId]);

  if (loading) {
    return <div className="text-center py-10">Loading player data...</div>;
  }

  if (!player) {
    return (
      <div className="text-center py-10">
        <h2 className="text-2xl font-bold mb-4">Player Not Found</h2>
        <p className="mb-4">Sorry, we couldn't find details for this player.</p>
        <Link to="/" className="text-blue-600 hover:underline">
          Return to Dashboard
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">{player.Player}</h1>

      <div className="bg-white p-6 rounded shadow mb-6">
        <h2 className="text-xl font-semibold mb-4">Player Information</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <p>
              <span className="font-medium">Position:</span> {player.Position}
            </p>
            <p>
              <span className="font-medium">College:</span> {player.College}
            </p>
            <p>
              <span className="font-medium">Draft:</span> {player.Draft}
            </p>
          </div>
          <div>
            <p>
              <span className="font-medium">RAS Score:</span>{" "}
              {player.RAS_numeric?.toFixed(2) || "N/A"}
            </p>
            <p>
              <span className="font-medium">Pro Bowl Selections:</span>{" "}
              {player.Pro_Bowls_numeric || "N/A"}
            </p>
            {player.Profile_URL && (
              <p>
                <a
                  href={player.Profile_URL}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:underline"
                >
                  View RAS Profile
                </a>
              </p>
            )}
          </div>
        </div>
      </div>

      <div className="text-center mt-6">
        <Link
          to="/"
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          Back to Dashboard
        </Link>
      </div>
    </div>
  );
};

export default PlayerDetails;
