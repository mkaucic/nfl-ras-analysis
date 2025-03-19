import React from "react";

const About = () => {
  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">About This Project</h1>

      <div className="bg-white p-6 rounded shadow mb-6">
        <h2 className="text-xl font-semibold mb-4">
          The Importance of RAS in the NFL Draft
        </h2>
        <p className="mb-4">
          This project explores the correlation between a player's Relative
          Athletic Score (RAS) and their likelihood of being selected for the
          Pro Bowl, one indicator of NFL success.
        </p>
        <p className="mb-4">
          RAS was developed by Kent Lee Platte as a metric to measure a player's
          athletic abilities compared to historical averages at their position.
          The score ranges from 0 to 10, with 10 being the most athletic and 5
          representing average athleticism.
        </p>
      </div>

      <div className="bg-white p-6 rounded shadow mb-6">
        <h2 className="text-xl font-semibold mb-4">Data Sources</h2>
        <p className="mb-4">
          The data for this project was collected from{" "}
          <a
            href="https://ras.football/"
            className="text-blue-600 hover:underline"
          >
            RAS.football
          </a>
          , specifically from their Pro Bowlers database. We analyzed
          information about NFL players who made the Pro Bowl, including their:
        </p>
        <ul className="list-disc pl-6 mb-4">
          <li>RAS scores</li>
          <li>Number of Pro Bowl selections</li>
          <li>College</li>
          <li>Draft information</li>
          <li>Position</li>
          <li>Physical measurements and athletic testing results</li>
        </ul>
      </div>

      <div className="bg-white p-6 rounded shadow">
        <h2 className="text-xl font-semibold mb-4">Methodology</h2>
        <p className="mb-4">
          We analyzed the relationship between RAS and Pro Bowl selections using
          statistical methods including correlation analysis and
          position-specific breakdowns. Our goal was to determine whether higher
          athletic testing scores correlate with on-field success as measured by
          Pro Bowl selections.
        </p>
        <p>
          The visualization tools on this site allow you to explore this data
          yourself, filtering by position and examining the relationship between
          athleticism and recognition as one of the league's best players.
        </p>
      </div>
    </div>
  );
};

export default About;
