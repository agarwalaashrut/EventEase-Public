.PHONY: help install install-backend install-frontend test test-backend test-frontend lint lint-backend lint-frontend format format-backend format-frontend docker-up docker-down clean

# Python executable to use when creating venvs. Can be overridden when calling make:
# make PYTHON=python install-backend
PYTHON ?= python3

help:
	@echo "EventEase - Available Commands"
	@echo "=============================="
	@echo ""
	@echo "Setup:"
	@echo "  make install           - Install all dependencies (backend + frontend)"
	@echo "  make install-backend   - Install backend dependencies"
	@echo "  make install-frontend  - Install frontend dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  make test             - Run all tests"
	@echo "  make test-backend     - Run backend tests"
	@echo "  make test-frontend    - Run frontend tests"
	@echo ""
	@echo "Linting:"
	@echo "  make lint             - Run all linters"
	@echo "  make lint-backend     - Run backend linters"
	@echo "  make lint-frontend    - Run frontend linters"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-up        - Start all services with Docker Compose"
	@echo "  make docker-down      - Stop all Docker services"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean            - Remove build artifacts and caches"

# Installation
install: install-backend install-frontend

install-backend:
	@echo "Installing backend dependencies..."
	cd backend && $(PYTHON) -m venv venv && \
	if [ -f venv/bin/python ]; then \
		venv/bin/python -m pip install -r requirements.txt; \
	else \
		venv/Scripts/python -m pip install -r requirements.txt; \
	fi

install-frontend:
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

# Testing
test: test-backend test-frontend

test-backend:
	@echo "Running backend tests..."
	cd backend && \
	if [ -f venv/bin/python ]; then \
		venv/bin/python -m pytest; \
	else \
		venv/Scripts/python -m pytest; \
	fi

test-frontend:
	@echo "Running frontend tests..."
	cd frontend && npm test -- --watchAll=false

# Linting
lint: lint-backend lint-frontend

lint-backend:
	@echo "Linting backend..."
	cd backend && \
	if [ -f venv/bin/python ]; then \
		venv/bin/python -m flake8 .; \
	else \
		venv/Scripts/python -m flake8 .; \
	fi

lint-frontend:
	@echo "Linting frontend..."
	cd frontend && npm run lint

# Docker
docker-up:
	@echo "Starting Docker services..."
	cd infra && docker compose --env-file .env up --build

docker-down:
	@echo "Stopping Docker services..."
	cd infra && docker compose down

# Cleanup
clean:
	@echo "Cleaning build artifacts..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "coverage" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "build" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "Cleanup complete!"
