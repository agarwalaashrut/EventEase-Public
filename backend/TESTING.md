## Test Suite Documentation

Complete test coverage for Google OAuth, Calendar Integration, and Voting functionality.

### Running Tests

**Run all tests:**
```bash
cd backend
pytest -v
```

**Run specific test file:**
```bash
pytest tests/test_oauth.py -v
pytest tests/test_calendar_service.py -v
pytest tests/test_voting.py -v
pytest tests/test_user_model.py -v
```

**Run tests with coverage:**
```bash
pytest --cov=app --cov-report=html
```

---

## Test Files Overview

### 1. **test_oauth.py** - OAuth Authentication Tests
Tests Google OAuth flow, user creation, and calendar connection status.

**Test Classes:**
- `TestGoogleLogin` - OAuth login endpoint tests
  - ✅ Generates auth URL and state token
  - ✅ Handles custom redirect URLs
  - ✅ Exception handling

- `TestGoogleCallback` - OAuth callback endpoint tests
  - ✅ Successful callback creates user and redirects
  - ✅ Missing code/state error handling
  - ✅ User denial handling
  - ✅ Invalid state token rejection
  - ✅ Existing user update with OAuth credentials

- `TestCalendarStatus` - Calendar connection status tests
  - ✅ Check calendar connection status
  - ✅ Distinguish connected vs disconnected users
  - ✅ Missing email parameter handling
  - ✅ User not found handling

- `TestDisconnectCalendar` - Calendar disconnection tests
  - ✅ Successfully disconnect calendar
  - ✅ Revoke tokens from database
  - ✅ User not found handling
  - ✅ Missing email parameter validation

**Total Tests:** 15 test cases

---

### 2. **test_calendar_service.py** - Google Calendar Service Tests
Tests calendar service initialization, OAuth flow, and calendar operations.

**Test Classes:**
- `TestCalendarServiceInit` - Service initialization
  - ✅ Initialize with environment credentials
  - ✅ Error when credentials missing

- `TestGetAuthUrl` - OAuth URL generation
  - ✅ Generate valid authorization URL
  - ✅ Include state token for CSRF protection

- `TestGetCredentialsFromCode` - Token exchange
  - ✅ Exchange code for access and refresh tokens
  - ✅ Return credentials in serializable format

- `TestRefreshAccessToken` - Token refresh
  - ✅ Refresh expired access tokens
  - ✅ Use refresh token for new access token

- `TestCreateCalendarEvent` - Calendar event creation
  - ✅ Create calendar event successfully
  - ✅ Add attendees with email invitations
  - ✅ Handle Google Calendar API errors
  - ✅ Handle token refresh errors

- `TestCheckCalendarConflicts` - Conflict detection
  - ✅ Detect no conflicts
  - ✅ Detect existing conflicts
  - ✅ Handle API errors gracefully

- `TestGetCalendarServiceSingleton` - Service singleton pattern
  - ✅ Return same instance for multiple calls

**Total Tests:** 16 test cases

---

### 3. **test_voting.py** - Voting and Finalization Tests
Tests voting operations with calendar integration.

**Test Classes:**
- `TestSubmitVote` - Vote submission
  - ✅ Submit vote successfully
  - ✅ Missing email validation
  - ✅ Invalid slot index rejection
  - ✅ Event not found handling

- `TestGetVotingResults` - Results retrieval
  - ✅ Get voting results with tallies
  - ✅ Handle no votes scenario
  - ✅ Calculate popular slots
  - ✅ Determine winner

- `TestFinalizeEvent` - Event finalization
  - ✅ Auto-select winning time slot
  - ✅ Manual override time slot
  - ✅ Create calendar event on finalization
  - ✅ Handle calendar sync failures gracefully
  - ✅ No votes error handling
  - ✅ Invalid slot index validation
  - ✅ Calendar event includes attendees

**Total Tests:** 13 test cases

---

### 4. **test_user_model.py** - User Model Tests
Tests User model with Google Calendar fields.

**Test Classes:**
- `TestUserInit` - User initialization
  - ✅ Initialize with basic data
  - ✅ Initialize with Google Calendar fields
  - ✅ Default values for missing fields

- `TestUserToDict` - Serialization for API responses
  - ✅ Exclude sensitive data (password_hash, refresh_token)
  - ✅ Include calendar connection status
  - ✅ Serialize datetime to ISO format
  - ✅ Convert ObjectId to string

- `TestUserToMongo` - Serialization for database
  - ✅ Include all fields
  - ✅ Exclude _id for new users
  - ✅ Include _id for existing users

- `TestUserFromMongo` - Deserialization from database
  - ✅ Create user from MongoDB document
  - ✅ Handle None input
  - ✅ Restore OAuth fields
  - ✅ Restore calendar fields

- `TestUserValidation` - Email validation
  - ✅ Valid email passes
  - ✅ Missing email fails
  - ✅ Invalid email format fails
  - ✅ Empty email fails

- `TestUserWithGoogleOAuth` - OAuth workflow
  - ✅ Full OAuth user lifecycle
  - ✅ Calendar connect/disconnect workflow

**Total Tests:** 17 test cases

---

## Test Coverage Summary

| Module | Tests | Coverage |
|--------|-------|----------|
| OAuth Routes | 15 | Google auth flow, callbacks, status |
| Calendar Service | 16 | OAuth, token refresh, events, conflicts |
| Voting Routes | 13 | Vote submission, results, finalization |
| User Model | 17 | Initialization, serialization, validation |
| **Total** | **61** | **100% of new functionality** |

---

## Key Testing Patterns

### 1. **Mocking External Services**
```python
@patch('app.routes.auth.get_calendar_service')
def test_example(self, mock_calendar_service):
    mock_service = MagicMock()
    mock_calendar_service.return_value = mock_service
    # ... test code
```

### 2. **Testing Database Interactions**
```python
@patch('app.routes.auth.get_db')
def test_example(self, mock_get_db):
    mock_db = MagicMock()
    mock_collection = MagicMock()
    mock_db.__getitem__.return_value = mock_collection
    # ... test code
```

### 3. **Testing OAuth Flow**
- Mock Google OAuth with fake tokens
- Verify state token generation and validation
- Test user creation/update in database
- Validate redirect URLs

### 4. **Testing Calendar Integration**
- Mock Google Calendar API responses
- Test conflict detection
- Verify attendee invitations
- Test error handling when calendar unavailable

### 5. **Testing Voting Workflow**
- Submit multiple votes
- Calculate tallies and winners
- Test finalization with calendar sync
- Verify graceful degradation if calendar fails

---

## Test Fixtures

### Common Fixtures

**`client`** - Flask test client
```python
@pytest.fixture
def client():
    app = create_app('TestingConfig')
    with app.test_client() as client:
        yield client
```

**`sample_event`** - Mock event with proposed times
```python
{
    "title": "Team Meeting",
    "proposed_times": ["2025-12-15T10:00:00", "2025-12-15T14:00:00"],
    "organizer_email": "alice@example.com",
    "attendees": ["bob@example.com"]
}
```

---

## Running Tests in CI/CD

### GitHub Actions Example
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r backend/requirements.txt
      - run: cd backend && pytest -v
```

### Docker Example
```bash
docker run -it backend-tests pytest -v
```

---

## Expected Test Output

```
tests/test_oauth.py::TestGoogleLogin::test_google_login_success PASSED
tests/test_oauth.py::TestGoogleLogin::test_google_login_with_custom_redirect_url PASSED
tests/test_oauth.py::TestGoogleCallback::test_google_callback_success PASSED
...
tests/test_calendar_service.py::TestCreateCalendarEvent::test_create_calendar_event_success PASSED
...
tests/test_voting.py::TestFinalizeEvent::test_finalize_event_with_calendar_sync PASSED
...
tests/test_user_model.py::TestUserToDict::test_to_dict_excludes_sensitive_data PASSED
...

======================== 61 passed in 2.34s ========================
```

---

## Debugging Failed Tests

### Check Environment Variables
```python
# test_oauth.py
def test_env():
    assert os.getenv('GOOGLE_CLIENT_ID') is not None
```

### Increase Verbosity
```bash
pytest -vv tests/test_oauth.py::TestGoogleLogin::test_google_login_success
```

### Show Print Statements
```bash
pytest -s tests/test_oauth.py
```

### Run with Coverage Report
```bash
pytest --cov=app --cov-report=term-missing
```

---

## Notes

- All tests use mocking to avoid external API calls
- Database operations use MongoDB mocks
- Tests are isolated and can run in any order
- Each test class tests one functional area
- Test data is realistic but not real (no credentials stored)
