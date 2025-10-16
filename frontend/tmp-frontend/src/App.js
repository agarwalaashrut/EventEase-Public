import React, { useState } from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";

import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Suggestions from "./pages/Suggestions";

import EventForm from "./pages/EventCreation";

function LandingPage() {
  const [showForm, setShowForm] = useState(false);

  return (
    <div className="LandingPage">
      {!showForm ? (
        // Landing Page
        <div style={{ textAlign: "center", marginTop: "100px" }}>
          <h1>Welcome to EventEase</h1>
          <h2>Insert little description here</h2> 
          <button
            onClick={() => setShowForm(true)}
            style={{
              padding: "15px 30px",
              fontSize: "16px",
              backgroundColor: "#007bff",
              color: "white",
              border: "none",
              borderRadius: "5px",
              cursor: "pointer",
              marginTop: "20px"
            }}
          >
            Create an Event
          </button>
        </div>
      ) : (
        // Event Form Screen
        <EventForm
          onCancel={() => setShowForm(false)}
          onCreate={() => setShowForm(false)} 
        />
      )}
    </div>
  );
}

function App() {
  return (
    <Router>
      <nav>
        <Link to="/">Home</Link> |{" "}
        <Link to="/login">Login</Link> |{" "}
        <Link to="/signup">Signup</Link> |{" "}
        <Link to="/suggestions">Suggestions</Link>
      </nav>

      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/suggestions" element={<Suggestions />} />
      </Routes>
    </Router>
  );
}

export default App;
