import { useState } from "react";
import { register } from "../api/auth";

export default function Signup() {
  const [form, setForm] = useState({ username: "", password: "" });
  const [message, setMessage] = useState("");

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await register(form);
      setMessage("Signup success (backend not connected yet)");
    } catch (err) {
      setMessage("Signup failed (no backend yet)");
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>Signup</h2>
      <input
        name="username"
        placeholder="Username"
        value={form.username}
        onChange={handleChange}
      />
      <input
        type="password"
        name="password"
        placeholder="Password"
        value={form.password}
        onChange={handleChange}
      />
      <button type="submit">Signup</button>
      <p>{message}</p>
    </form>
  );
}
