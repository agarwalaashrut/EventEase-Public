# EventEase

A full-stack event planning application where users can create events, suggest times and locations, vote on preferences, and sync finalized events to Google Calendar.

---

## Table of Contents

- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Development Workflow](#development-workflow)
- [Application Architecture](#application-architecture)
- [Testing](#testing)
- [Contributing](#contributing)
- [Next Steps](#next-steps)
- [Additional Resources](#additional-resources)

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Backend** | Flask | Python web framework |
| | PyMongo | MongoDB integration |
| | Flask-SocketIO | Real-time WebSocket communication |
| | Flask-CORS | Cross-origin resource sharing |
| | Authlib | OAuth2 authentication (Google Calendar) |
| **Frontend** | React | UI library |
| | React Router | Client-side routing |
| | Bootstrap 5 | CSS framework with React-Bootstrap |
| | Socket.IO Client | Real-time WebSocket client |
| **Database** | MongoDB Atlas | Cloud-hosted NoSQL database |
| **Infrastructure** | Docker & Docker Compose | Containerization and orchestration |

---

## Project Structure

```
fa25-fa25-team080/
├── backend/                    # Flask API server
│   ├── app/
│   │   ├── __init__.py        # Flask app factory
│   │   ├── config.py          # Configuration management
│   │   ├── models/            # Database models (Event, User, etc.)
│   │   │   ├── event.py       # Event model schema
│   │   │   └── __init__.py
│   │   ├── routes/            # API endpoints
│   │   │   ├── events.py      # Event CRUD operations
│   │   │   └── __init__.py
│   │   └── services/          # Business logic layer
│   │       └── __init__.py
│   ├── tests/                 # Pytest test suite
│   │   └── test_health.py
│   ├── run.py                 # Application entry point
│   ├── requirements.txt       # Python dependencies
│   └── pytest.ini             # Test configuration
│
├── frontend/                   # React application
│   ├── src/
│   │   ├── components/        # Reusable UI components
│   │   │   ├── NavigationBar.js
│   │   │   └── index.js
│   │   ├── pages/             # Page-level components
│   │   │   ├── HomePage.js
│   │   │   ├── EventsPage.js
│   │   │   └── index.js
│   │   ├── services/          # API and WebSocket clients
│   │   │   ├── api.js         # HTTP API calls
│   │   │   └── websocket.js   # Socket.IO connection
│   │   ├── hooks/             # Custom React hooks
│   │   ├── state/             # State management (Context/Redux)
│   │   ├── styles/            # Custom CSS
│   │   └── tests/             # Jest + React Testing Library
│   ├── public/                # Static assets
│   └── package.json           # Node dependencies
│
├── infra/                      # Docker infrastructure
│   ├── Dockerfile.backend     # Backend container image
│   ├── Dockerfile.frontend    # Frontend container image
│   ├── docker-compose.yml     # Multi-service orchestration
│   └── .env.example           # Environment variables template
│
├── Makefile                    # Common development commands
└── README.md                   # Project documentation
```

---

## Prerequisites

Before starting, ensure you have the following installed:

- **Docker**
- **Python 3.11+** (for local development)
- **Node.js 20+** and **npm** (for local development)

---

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd fa25-fa25-team080
```

### 2. Configure Environment Variables

Create `.env` files from the examples and populate with actual values:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
cp infra/.env.example infra/.env
```

> **Note:** Never commit real secrets to version control.

**Required Configuration:**
- `MONGO_URI` - MongoDB Atlas connection string
- `SECRET_KEY` - Flask session secret
- `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` - OAuth credentials

(ask for in team Discord)

### 3. Start the Application (Docker - Recommended)

Use the Makefile for simplified commands:

```bash
make install          # Install dependencies (first time only)
make docker-up        # Start all services with Docker
```

> **Note:** The Makefile is cross-platform compatible (macOS, Linux, Windows). It automatically detects the correct virtual environment paths. If needed, you can specify a specific Python executable, e.g., `make PYTHON=python install`

**Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:5001
  - Health Check: http://localhost:5001/health
  - Event API: http://localhost:5001/api/events
  - ...

**Stop services:**
- Press `Ctrl+C` in the terminal to stop running containers
- Run `make docker-down` to stop and remove containers (useful for a clean restart)

### 4. Run Tests

```bash
make test             # Run all tests (backend + frontend)
make test-backend     # Backend tests only
make test-frontend    # Frontend tests only
```

### 5. Additional Makefile Commands

```bash
make help            # Show all available commands
make lint            # Run linters on all code
make clean           # Remove build artifacts and caches
```

---

## Development Workflow

### Manual Development (Without Docker)

If you prefer running services individually (not recommended):

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate              # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py                          # Runs on http://localhost:5001
```

#### Frontend

```bash
cd frontend
npm install
npm start                              # Runs on http://localhost:3000
```

**Note:** You'll need MongoDB Atlas configured (not local MongoDB) as specified in your `.env` files.

---

## Application Architecture

### Data Flow

#### Backend Request Flow
```
Client Request → Flask Route → Service Layer → MongoDB Model → Database
                     ↓              ↓              ↓
                 Validation    Business Logic   Data Access
                     ↓              ↓              ↓
                 Response ← Transform Data ← Query Results
```

#### Frontend Component Flow
```
User Interaction → Component → API Service → Backend Endpoint
                      ↓             ↓
                  State Update   HTTP/WebSocket
                      ↓             ↓
                  Re-render ← Response Data
```

### Key Components

**Backend (`backend/app/`):**
- `models/` - MongoDB schemas and data models (Mongoose-style with PyMongo)
- `routes/` - Flask blueprints for API endpoints (e.g., `/api/events`)
- `services/` - Business logic layer (event creation, voting, calendar sync)
- `config.py` - Environment-based configuration

**Frontend (`frontend/src/`):**
- `components/` - Reusable UI elements (NavigationBar, EventCard, etc.)
- `pages/` - Top-level route components (HomePage, EventsPage)
- `services/api.js` - Centralized HTTP client for backend communication
- `services/websocket.js` - Socket.IO client for real-time updates

### Real-Time Features

WebSocket communication (Flask-SocketIO + Socket.IO Client) enables:
- Live voting updates
- Real-time event changes
- Collaborative time slot selection

---

## Testing

### Running Tests

```bash
# All tests
make test

# Backend only (pytest)
make test-backend
cd backend && pytest

# Frontend only (Jest + React Testing Library)
make test-frontend
cd frontend && npm test -- --watchAll=false

# With coverage
cd backend && pytest --cov=app --cov-report=html
cd frontend && npm test -- --coverage --watchAll=false
```

### Test Structure

**Backend (`backend/tests/`):**
- Unit tests for models, routes, and services
- Integration tests with MongoDB test database
- Use pytest fixtures for setup/teardown

**Frontend (`frontend/src/tests/`):**
- Component tests with React Testing Library
- Mock API calls and WebSocket connections
- Test user interactions and state changes

### Linting

```bash
make lint              # Lint all code
make lint-backend      # Flake8 (Python)
make lint-frontend     # ESLint (JavaScript)
```

---

## Contributing

### Branch Workflow

1. **Clone and pull latest changes:**
   ```bash
   git clone <repository-url>
   cd fa25-fa25-team080
   git checkout main
   git pull origin main
   ```

2. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```
   
   **Branch naming conventions:**
   - `feature/` - New features
   - `bugfix/` - Bug fixes
   - `hotfix/` - Critical production fixes
   - `docs/` - Documentation updates
   - `refactor/` - Code refactoring
   - `test/` - Test additions/updates

3. **Make your changes:**
   - Write code following project standards
   - Add tests for new functionality
   - Update documentation as needed

4. **Test your changes:**
   ```bash
   make test
   make lint
   ```

5. **Commit with descriptive messages:**
   ```bash
   git add .
   git commit -m "feat: add event voting functionality"
   ```
   
   **Commit message prefixes:**
   - `feat:` - New feature
   - `fix:` - Bug fix
   - `docs:` - Documentation changes
   - `test:` - Test additions/changes
   - `refactor:` - Code refactoring
   - `style:` - Formatting changes

6. **Push to GitHub:**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request:**
   - Go to GitHub repository
   - Click "New Pull Request"
   - Request reviews from teammates
   - Address any feedback

---

## Next Steps

### Core Features to Implement

1. **Database Models** (`backend/app/models/`)
   - User model (authentication, profile)
   - Event model (title, description, creator)
   - Vote model (time slots, location preferences)
   - Participant model (RSVP status)

2. **API Endpoints** (`backend/app/routes/`)
   - CRUD operations
   - Voting endpoints
   - User authentication routes
   - Calendar sync endpoints

3. **Business Logic** (`backend/app/services/`)
   - Event creation and management
   - Voting aggregation and consensus
   - Google Calendar integration

4. **Frontend Components** (`frontend/src/components/`)
   - EventCard - Display event details
   - VotingWidget - Time/location voting interface
   - TimeSlotPicker - Interactive time selection
   - LocationSuggester - Location proposal tool

5. **State Management** (`frontend/src/state/`)
   - Context API or Redux for global state
   - User authentication state
   - Event data caching

6. **Authentication**
   - Google OAuth 2.0 setup
   - Session management
   - Protected routes

7. **Real-Time Features**
   - Socket.IO event handlers
   - Live voting updates
   - Real-time notifications

8. **Google Calendar Integration**
   - OAuth flow implementation
   - Calendar event creation
   - Event sync on finalization

### Future Enhancements

- **Background Tasks:** Celery with Redis for asynchronous calendar syncing
- **Caching:** Redis for session storage and response caching
- **Email Notifications:** SendGrid or similar for event reminders
- **Mobile App:** React Native version
- **Analytics:** Event engagement metrics

---

## Additional Resources

### Documentation
- [Flask Documentation](https://flask.palletsprojects.com/)
- [React Documentation](https://react.dev/)
- [MongoDB Atlas Guide](https://docs.atlas.mongodb.com/)
- [Socket.IO Documentation](https://socket.io/docs/)
- [Docker Compose Reference](https://docs.docker.com/compose/)

### API Development
- [RESTful API Design Best Practices](https://restfulapi.net/)
- [Google Calendar API](https://developers.google.com/calendar)
- [OAuth 2.0 Guide](https://oauth.net/2/)

### Testing
- [Pytest Documentation](https://docs.pytest.org/)
- [React Testing Library](https://testing-library.com/react)

---

## **Team 080** - Fall 2025

- Alex Gorczowski (frontend)
- Omosefe Edomwande (frontend)
- Aashrut Agarwal (backend)
- Sam Barbeau (backend)