## Google OAuth + Calendar Integration - Implementation Summary

### Overview
Implemented complete Google Calendar OAuth integration that allows users to automatically sync finalized events to their Google Calendar with attendee invitations.

---

## Backend Changes

### 1. **New: `backend/app/services/calendar_service.py`**
Complete Google Calendar service with OAuth 2.0 flow:

**Features:**
- `get_auth_url()` - Generate OAuth authorization URL with CSRF protection
- `get_credentials_from_code()` - Exchange authorization code for refresh/access tokens
- `refresh_access_token()` - Refresh expired access tokens using refresh token
- `create_calendar_event()` - Create calendar events with attendee invitations
- `check_calendar_conflicts()` - Detect time conflicts on user's calendar

**Key Properties:**
- Scopes: `https://www.googleapis.com/auth/calendar`
- Handles token refresh automatically
- Returns structured responses with error messages
- Singleton instance for efficiency

---

### 2. **New: `backend/app/routes/auth.py`**
OAuth authentication routes:

**Endpoints:**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/auth/google/login` | GET | Initiate OAuth flow, returns auth URL |
| `/api/auth/google/callback` | GET | Handle OAuth callback, exchange code for tokens, create/update user |
| `/api/auth/calendar/status` | GET | Check if user has calendar connected |
| `/api/auth/calendar/disconnect` | POST | Revoke calendar access |

**Callback Flow:**
1. Exchanges authorization code for OAuth credentials
2. Retrieves user info from Google (email, name)
3. Creates new user or updates existing user with Google credentials
4. Stores refresh token in database for future use
5. Returns user data and redirect URL

---

### 3. **Updated: `backend/app/models/user.py`**
Added Google Calendar fields:
```python
self.google_refresh_token      # OAuth refresh token for persistent API access
self.google_calendar_id         # User's calendar ID (usually their email)
```

**Changes to methods:**
- `to_dict()` - Added `google_calendar_connected` boolean flag
- `to_mongo()` - Now persists Google credentials

---

### 4. **Updated: `backend/app/routes/voting.py`**
Enhanced finalize endpoint with calendar integration:

**New Behavior:**
- When event is finalized, checks if organizer has Google Calendar connected
- Automatically creates calendar event with:
  - Event title, description, organizer
  - Finalized time slot from voting results
  - All attendees invited (organizer + attendee_emails)
  - Automatic email notifications to attendees
- Stores `google_calendar_event_id` in event document for reference
- Returns calendar response in finalize response:
  ```json
  {
    "calendar": {
      "calendar_event_created": true,
      "calendar_event_id": "google_event_xyz",
      "calendar_error": null
    }
  }
  ```

**Error Handling:**
- Event finalization succeeds even if calendar sync fails
- Calendar errors are reported but don't block finalization
- Detailed error messages returned to frontend

---

### 5. **Updated: `backend/requirements.txt`**
Added Google Calendar API dependencies:
```
google-auth-oauthlib==1.2.0
google-auth-httplib2==0.2.0
google-api-python-client==2.100.0
```

---

### 6. **Updated: `backend/app/__init__.py`**
Registered new auth blueprint:
```python
from app.routes import auth_bp
app.register_blueprint(auth_bp)
```

---

### 7. **Updated: `backend/app/routes/__init__.py`**
Exported auth_bp for blueprint registration

---

## Frontend Changes

### Updated: `frontend/src/services/api.js`

**New `auth` namespace with methods:**

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `getGoogleLoginUrl(redirectUrl)` | GET `/api/auth/google/login` | Get OAuth URL |
| `getCalendarStatus(email)` | GET `/api/auth/calendar/status` | Check calendar connection |
| `disconnectCalendar(email)` | POST `/api/auth/calendar/disconnect` | Disconnect calendar |

**Example Usage:**
```javascript
// Initiate OAuth
const result = await api.auth.getGoogleLoginUrl();
window.location.href = result.auth_url;

// Check status
const status = await api.auth.getCalendarStatus("user@example.com");
if (status.calendar_connected) {
  console.log("Calendar connected!");
}

// Disconnect
await api.auth.disconnectCalendar("user@example.com");
```

**Enhanced Voting Documentation:**
- Updated `finalizeEvent()` documentation to show calendar response
- Added examples of checking calendar event creation status
- Documented that finalization succeeds even if calendar sync fails

---

## Configuration

### Required Environment Variables (in `.env`):
```dotenv
GOOGLE_CLIENT_ID=your-client-id-from-google-console
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:5001/api/auth/callback
```

### Getting Google OAuth Credentials:
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create new project or select existing
3. Enable Google Calendar API
4. Create OAuth 2.0 credentials (Desktop application or Web application)
5. Add authorized redirect URI: `http://localhost:5001/api/auth/callback`
6. Copy Client ID and Client Secret to `.env`

---

## Database Changes

### User Collection Updates
New fields added to user documents:
```json
{
  "email": "user@example.com",
  "name": "John Doe",
  "google_refresh_token": "1//0gFfoo...",
  "google_calendar_id": "user@example.com",
  "oauth_provider": "google",
  "oauth_id": "google_user_id_123"
}
```

### Event Collection Updates
New field when calendar event is created:
```json
{
  "_id": "event_id",
  "google_calendar_event_id": "google_event_id_xyz"
}
```

---

## Testing Checklist

### OAuth Flow:
- [ ] `/api/auth/google/login` returns valid auth URL
- [ ] User can authorize app in Google
- [ ] Callback exchanges code for tokens
- [ ] User created/updated in database with refresh token
- [ ] State token validated (CSRF protection)

### Calendar Integration:
- [ ] Event finalization creates calendar event
- [ ] Calendar event has correct title, time, description
- [ ] Attendees receive calendar invitations
- [ ] Organizer without calendar connection: event still finalizes
- [ ] Conflict detection works (if implemented in UI)

### API Status Checks:
- [ ] `/api/auth/calendar/status` returns correct connection status
- [ ] `/api/auth/calendar/disconnect` revokes access
- [ ] Refresh token handles expiration automatically

---

## Frontend Integration Steps

### For Calendar Connection UI:
1. Add button "Connect Google Calendar" in user settings
2. Call `api.auth.getGoogleLoginUrl()` on button click
3. Redirect to OAuth URL returned
4. After OAuth callback, show confirmation
5. Check connection status with `api.auth.getCalendarStatus(email)`
6. Show "Disconnect Calendar" option if connected

### For Event Finalization:
1. When finalizing event, show spinner
2. Call `api.voting.finalizeEvent(eventId)`
3. Check `response.calendar.calendar_event_created`
4. Show toast: "Event finalized and added to calendar!" or warning if calendar sync failed

---

## Security Notes

1. **Refresh tokens** stored securely in MongoDB (not transmitted to frontend)
2. **State tokens** used for CSRF protection in OAuth flow
3. **Access tokens** never stored permanently (generated on-demand from refresh token)
4. **Scopes** limited to `calendar` (no access to Gmail, Drive, etc.)
5. **Attendee notifications** sent through Google (automatic)

---

## Future Enhancements

1. **Conflict Detection UI**: Use `check_calendar_conflicts()` to warn organizers
2. **Calendar Sync History**: Track which events were synced
3. **Revoke Consent**: Handle Google account revocation
4. **Multiple Calendars**: Allow selection of target calendar (not just primary)
5. **Event Modifications**: Update calendar event if meeting time changes
6. **RSVP Integration**: Sync Google Calendar RSVP status back to app
