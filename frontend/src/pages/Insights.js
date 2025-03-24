import React, { useState, useEffect } from "react";
import { Tab, Tabs, TabList, TabPanel } from "react-tabs";
import "react-tabs/style/react-tabs.css";
import HeatmapChart from "../components/HeatmapChart";
import PositionInsights from "../components/PositionInsights";

const Insights = () => {
  const [correlationData, setCorrelationData] = useState(null);
  const [positionData, setPositionData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);

    // Try to load data files
    const loadData = async () => {
      try {
        // Use sample data as fallback if files don't exist yet
        let corrData;
        let posData;

        try {
          const corrResponse = await fetch(
            "/data/measurement_correlation.json"
          );
          if (corrResponse.ok) {
            corrData = await corrResponse.json();
          } else {
            console.warn("Correlation data not available, using sample data");
            corrData = generateSampleCorrelationData();
          }
        } catch (e) {
          console.warn("Error loading correlation data:", e);
          corrData = generateSampleCorrelationData();
        }

        try {
          const posResponse = await fetch("/data/position_stats.json");
          if (posResponse.ok) {
            posData = await posResponse.json();
          } else {
            console.warn("Position data not available, using sample data");
            posData = generateSamplePositionData();
          }
        } catch (e) {
          console.warn("Error loading position data:", e);
          posData = generateSamplePositionData();
        }

        setCorrelationData(corrData);
        setPositionData(posData);
        setLoading(false);
      } catch (err) {
        console.error("Failed to load data:", err);
        setError("Failed to load insight data. Please try again later.");
        setLoading(false);
      }
    };

    loadData();
  }, []);

  // Generate sample correlation data for development/testing
  const generateSampleCorrelationData = () => {
    const measures = [
      "RAS_numeric",
      "Height",
      "Weight",
      "Speed",
      "Pro_Bowl_Count",
    ];
    const data = {};

    measures.forEach((m1) => {
      data[m1] = {};
      measures.forEach((m2) => {
        // Generate random correlation between -1 and 1
        // Diagonal values (self-correlation) are always 1
        data[m1][m2] =
          m1 === m2 ? 1 : Math.round((Math.random() * 2 - 1) * 100) / 100;
      });
    });

    return data;
  };

  // Generate sample position data for development/testing
  const generateSamplePositionData = () => {
    const positions = [
      "QB",
      "RB",
      "WR",
      "TE",
      "OT",
      "OG",
      "C",
      "DE",
      "DT",
      "LB",
      "CB",
      "S",
    ];
    return positions.map((pos) => ({
      Position: pos,
      PlayerCount: Math.floor(Math.random() * 50) + 10,
      AvgRAS: Math.round((Math.random() * 4 + 6) * 100) / 100, // 6-10 range
      AvgProBowls: Math.round((Math.random() * 3 + 1) * 100) / 100, // 1-4 range
      TotalProBowls: Math.floor(Math.random() * 100) + 20,
      MultiProBowlRate: Math.round(Math.random() * 70) + 30, // 30-100 range
    }));
  };

  if (loading) {
    return <div className="text-center py-10">Loading insights data...</div>;
  }

  if (error) {
    return <div className="text-center py-10 text-red-600">{error}</div>;
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">In-Depth RAS Insights</h1>

      <Tabs>
        <TabList className="flex mb-4 border-b">
          <Tab className="px-4 py-2 bg-gray-100 rounded-t-lg mr-2 cursor-pointer">
            Measurement Correlations
          </Tab>
          <Tab className="px-4 py-2 bg-gray-100 rounded-t-lg mr-2 cursor-pointer">
            Position Analysis
          </Tab>
        </TabList>

        <TabPanel>
          <div className="bg-white p-6 rounded shadow mb-8">
            <h2 className="text-xl font-semibold mb-4">
              Athletic Measurement Correlations
            </h2>
            <p className="mb-6">
              This heatmap shows how different athletic measurements correlate
              with Pro Bowl success. Darker red indicates a stronger positive
              correlation, while darker blue shows a negative correlation.
            </p>
            <HeatmapChart data={correlationData} />
          </div>
        </TabPanel>

        <TabPanel>
          <div className="bg-white p-6 rounded shadow mb-8">
            <h2 className="text-xl font-semibold mb-4">
              Position-Specific Analysis
            </h2>
            <p className="mb-6">
              Explore how RAS impacts Pro Bowl likelihood for each position.
              Select a position below to see detailed insights.
            </p>
            <PositionInsights positionData={positionData} />
          </div>
        </TabPanel>
      </Tabs>
    </div>
  );
};

export default Insights;
