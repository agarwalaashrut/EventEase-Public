import React from "react";

function EventForm({ onCancel, onCreate} ) { 
  return (
    <div style={{ maxWidth: "500px", margin: "20px auto", padding: "20px", border: "1px solid #ccc", borderRadius: "8px" }}>
      <h1 style={{ textAlign: "center" }}>Create a New Event</h1>

      {/* Name input */}
      <div style={{ marginTop: "20px" }}>
        <label>Name of Event</label>
        <input
          type="text"
          placeholder="Enter event name"
          style={{ width: "100%", padding: "8px", marginTop: "5px" }}
        />
      </div>

      {/* Time input */}
      <div style={{ marginTop: "15px" }}>
        <label>Time:</label>
        <input
          type="datetime-local"
          style={{ width: "100%", padding: "8px", marginTop: "5px" }}
          
        />
      </div>

      {/* Invites */}
      <div style={{ marginTop: "15px" }}>
        <label>Invites:</label>
        <textarea
          placeholder="Enter emails separated by commas"
          style={{ width: "100%", padding: "8px", marginTop: "5px" }}
        />
      </div>

      {/* Buttons */}
      <div style={{ display: "flex", gap: "10px", marginTop: "20px" }}>
        <button
          style={{
            flex: 1,
            padding: "10px",
            backgroundColor: "#ff002fff",
            color: "white",
            border: "none",
            borderRadius: "5px"
          }}
          onClick={onCancel} 
        >
          Cancel
        </button>

        <button
          style={{
            flex: 1,
            padding: "10px",
            backgroundColor: "#007bff",
            color: "white",
            border: "none",
            borderRadius: "5px"
          }}
          onClick={onCreate}
        >
          Create Event
        </button>
      </div>
    </div>
  );
}

export default EventForm;
