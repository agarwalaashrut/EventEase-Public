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
    /**
     * POST /api/events/:id/invite
     * Required: { emails: ["user1@example.com", "user2@example.com"] }
     * Returns: { success: true, message, invited: [...], not_found: [...] }
     */
    invite: async (eventId, emails) => {
      const response = await fetch(`${API_BASE_URL}/api/events/${eventId}/invite`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ emails }),
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

  // Invitations endpoints
  invitations: {
    /**
     * GET /api/invitations?email=user@example.com
     * Required query param: email
     * Returns: { success: true, invitations: [{event_id, event_title, organizer, status, invited_at, event_details: {...}}] }
     */
    getForUser: async (email) => {
      const response = await fetch(`${API_BASE_URL}/api/invitations?email=${encodeURIComponent(email)}`);
      return response.json();
    },

    /**
     * POST /api/invitations/:id/respond
     * Required: { email, response: "accepted" | "declined" }
     * Returns: { success: true, message }
     * Note: Updates user's invitations array and event's attendees list
     */
    respond: async (invitationId, email, responseType) => {
      const response = await fetch(`${API_BASE_URL}/api/invitations/${invitationId}/respond`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, response: responseType }),
      });
      return response.json();
    },
  },

  // Voting endpoints
  voting: {
    /**
     * POST /api/events/:id/vote
     * Required: { user_email, time_slot_indexes: [0, 2] }
     * Returns: { success: true, message, votes: {...} }
     */
    submitVote: async (eventId, userEmail, timeSlotIndexes) => {
      const response = await fetch(`${API_BASE_URL}/api/events/${eventId}/vote`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_email: userEmail,
          time_slot_indexes: timeSlotIndexes,
        }),
      });
      return response.json();
    },

    /**
     * GET /api/events/:id/votes
     * Returns: { success: true, votes_by_user, votes_by_time_slot, popular_time_slots, total_votes, total_participants, proposed_times }
     */
    getVotingResults: async (eventId) => {
      const response = await fetch(`${API_BASE_URL}/api/events/${eventId}/votes`);
      return response.json();
    },

    /**
     * POST /api/events/:id/finalize
     * Optional: { time_slot_index }
     * Returns: { success: true, message, finalized_time_slot_index, finalized_time_slot, event: {...} }
     */
    finalizeEvent: async (eventId, timeSlotIndex = null) => {
      const body = {};
      if (timeSlotIndex !== null) {
        body.time_slot_index = timeSlotIndex;
      }
      const response = await fetch(`${API_BASE_URL}/api/events/${eventId}/finalize`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      return response.json();
    },
  },
};

export default api;
