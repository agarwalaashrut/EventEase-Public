/**
 * API Service Module for Backend Communication
 * Base URL: http://localhost:5001 (development)
 * 
 * Response Format:
 * - Success: { success: true, ... }
 * - Error: { success: false, error: "message" }
 */

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5001';

export const api = {
  // GET /health - Returns { status: 'ok' }
  healthCheck: async () => {
    const response = await fetch(`${API_BASE_URL}/health`);
    return response.json();
  },

  // Events endpoints
  events: {
    /**
     * GET /api/events
     * Returns: { success: true, count: number, events: [...] }
     * 
     * Event object: { _id, title, description, organizer, organizer_email, location,
     *                 proposed_times: [], attendees: [], status, created_at, votes: {} }
     */
    getAll: async () => {
      const response = await fetch(`${API_BASE_URL}/api/events`);
      return response.json();
    },

    /**
     * GET /api/events/:id
     * Returns: { success: true, event: {...} }
     */
    getById: async (eventId) => {
      const response = await fetch(`${API_BASE_URL}/api/events/${eventId}`);
      return response.json();
    },

    /**
     * POST /api/events
     * Required: { title, organizer_email, location }
     * Optional: { description, organizer, proposed_times: [], attendees: [] }
     * Returns: { success: true, message, event: {...} }
     */
    create: async (eventData) => {
      const response = await fetch(`${API_BASE_URL}/api/events`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(eventData),
      });
      return response.json();
    },
  },

  // Users endpoints
  users: {
    /**
     * POST /api/users/login
     * Required: { email, password }
     * Returns: { success: true, message, user: { _id, email, name, oauth_provider, created_at, last_login, invitations: [] } }
     * Error: { success: false, error: "Invalid email or password" } (401)
     */
    login: async (credentials) => {
      const response = await fetch(`${API_BASE_URL}/api/users/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(credentials),
      });
      return response.json();
    },

    /**
     * POST /api/users/register
     * Required: { email, password }
     * Optional: { name }
     * Returns: { success: true, message, user: {...} }
     * Error: { success: false, error: "User with this email already exists" } (409)
     * Note: Passwords are hashed with SHA-256 on backend. User object does NOT include password_hash.
     */
    register: async (userData) => {
      const response = await fetch(`${API_BASE_URL}/api/users/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData),
      });
      return response.json();
    },

    // Future implementation:
    // OAuth endpoint available on backend at POST /api/users/oauth/login
    // Required: { provider, oauth_id, email, name }
  },
};

export default api;
