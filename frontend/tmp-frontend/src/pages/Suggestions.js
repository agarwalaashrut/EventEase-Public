import { useState } from "react";

export default function Suggestions() {
  const [form, setForm] = useState({ time: "", location: "" });
  const [suggestions, setSuggestions] = useState([]);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!form.time || !form.location) return;

    setSuggestions([...suggestions, form]);
    setForm({ time: "", location: "" });
  };

  return (
    <div style={{ padding: "1rem" }}>
      <h2>Time & Location Suggestions</h2>

      <form onSubmit={handleSubmit} style={{ marginBottom: "1rem" }}>
        <input
          name="time"
          placeholder="Enter time (e.g. 3:00 PM, Friday)"
          value={form.time}
          onChange={handleChange}
          style={{ marginRight: "0.5rem" }}
        />
        <input
          name="location"
          placeholder="Enter location (e.g. Siebel 1404)"
          value={form.location}
          onChange={handleChange}
          style={{ marginRight: "0.5rem" }}
        />
        <button type="submit">Add</button>
      </form>

      <ul>
        {suggestions.map((s, idx) => (
          <li key={idx}>
            <strong>Time:</strong> {s.time} <br />
            <strong>Location:</strong> {s.location}
          </li>
        ))}
      </ul>
    </div>
  );
}
