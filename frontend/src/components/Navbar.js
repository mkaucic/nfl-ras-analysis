import React from "react";
import { Link } from "react-router-dom";

const Navbar = () => {
  return (
    <nav className="bg-blue-800 text-white p-4">
      <div className="container mx-auto flex justify-between items-center">
        <Link to="/" className="text-xl font-bold">
          NFL RAS Analysis
        </Link>
        <div className="space-x-4">
          <Link to="/" className="hover:text-blue-200">
            Dashboard
          </Link>
          <Link to="/analytics" className="hover:text-blue-200">
            Advanced Analytics
          </Link>
          <Link to="/about" className="hover:text-blue-200">
            About
          </Link>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
