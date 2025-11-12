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
     * Submit a vote for a single time slot. User can change their vote by calling again.
     * 
     * When to call:
     * - When user selects a single preferred time slot and clicks "Vote"
     * - When user changes their vote (submitting replaces the previous vote)
     * 
     * Required: { user_email, time_slot_index: 0 }
     * Returns: { success: true, message, votes: {...all votes}, tallies: {0: 2, 1: 1, 2: 2} }
     * 
     * Example:
     * const result = await api.voting.submitVote(
     *   "event123",
     *   "alice@company.com",
     *   1  // Single slot index
     * );
     */
    submitVote: async (eventId, userEmail, timeSlotIndex) => {
      const response = await fetch(`${API_BASE_URL}/api/events/${eventId}/vote`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_email: userEmail,
          time_slot_index: timeSlotIndex,
        }),
      });
      return response.json();
    },

    /**
     * GET /api/events/:id/votes
     * Get comprehensive voting results and statistics.
     * 
     * When to call:
     * - After submitting a vote to see updated tallies
     * - Periodically to refresh voting board/results page
     * - To determine current winning time slot before finalization
     * - Before the organizer finalizes the event
     * 
     * Returns: {
     *   success: true,
     *   votes_by_user: { "alice@ex.com": 0, "bob@ex.com": 1 },
     *   votes_by_time_slot: { 0: 2, 1: 1, 2: 1 },
     *   popular_time_slots: [
     *     { time_slot_index: 0, vote_count: 2, time_slot: "2025-11-14T10:00" },
     *     { time_slot_index: 1, vote_count: 1, time_slot: "2025-11-14T14:00" },
     *     { time_slot_index: 2, vote_count: 1, time_slot: "2025-11-15T10:00" }
     *   ],
     *   winner: 0,
     *   winner_context: {
     *     reason: "clear_winner",
     *     candidates: [0],
     *     total_votes: 4,
     *     total_participants: 3
     *   },
     *   total_votes: 4,
     *   total_participants: 3,
     *   proposed_times: ["2025-11-14T10:00", "2025-11-14T14:00", "2025-11-15T10:00"]
     * }
     * 
     * Example:
     * const results = await api.voting.getVotingResults("event123");
     * console.log(`Most popular: ${results.popular_time_slots[0].time_slot}`);
     * console.log(`Current winner: slot ${results.winner}`);
     * if (results.winner_context.reason === 'no_votes') {
     *   console.log('No votes yet - voting is in progress');
     * }
     */
    getVotingResults: async (eventId) => {
      const response = await fetch(`${API_BASE_URL}/api/events/${eventId}/votes`);
      return response.json();
    },

    /**
     * POST /api/events/:id/finalize
     * Finalize event with the winning time slot. Changes event status to "confirmed".
     * 
     * When to call:
     * - Organizer clicks "Finalize Event" button
     * - Voting period has ended
     * - All attendees have voted (or timeout reached)
     * 
     * Behavior:
     * - If time_slot_index provided: uses that (admin override)
     * - If not provided: automatically selects slot with most votes
     *   - Tie-break: picks lowest index deterministically
     * - Sets event.status = "confirmed"
     * - Sets event.finalized_time_slot = winning_index
     * 
     * Optional: { time_slot_index: 1 }  // Leave empty or omit for auto-selection
     * Returns: {
     *   success: true,
     *   message: "Event finalized successfully",
     *   finalized_time_slot_index: 0,
     *   finalized_time_slot: "2025-11-14T10:00",
     *   event: { ...full event object with finalized_time_slot, status: "confirmed" }
     * }
     * 
     * Error scenarios:
     * - No votes yet: error with context.reason = "no_votes"
     * - Tie and no majority: error with context.reason = "no_majority"
     * - Invalid time_slot_index: 400 error
     * 
     * Example (auto-select):
     * const result = await api.voting.finalizeEvent("event123");
     * if (result.success) {
     *   console.log(`Event confirmed for ${result.finalized_time_slot}`);
     * }
     * 
     * Example (manual override):
     * const result = await api.voting.finalizeEvent("event123", 2);
     * if (result.success) {
     *   console.log(`Event confirmed (organizer override) for slot ${result.finalized_time_slot_index}`);
     * }
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
