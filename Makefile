# NBU Newsletter Generator — one-command dev environment.
#
#   make dev        start backend (:8000) + frontend (:3000) together
#   make backend    backend only
#   make frontend   frontend only
#   make install    install backend + frontend deps + Playwright chromium
#   make test       backend tests
#   make docker     docker compose up --build

.PHONY: dev backend frontend install install-backend install-frontend test docker clean

PYTHON ?= python3
VENV := backend/.venv
PIP := $(VENV)/bin/pip
PY := $(VENV)/bin/python

install: install-backend install-frontend

install-backend:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r backend/requirements.txt
	$(PY) -m playwright install chromium

install-frontend:
	cd frontend && npm install

backend:
	cd backend && ../$(VENV)/bin/uvicorn app.main:app --reload --port 8000

frontend:
	cd frontend && npm run dev

# Run both; Ctrl-C stops both.
dev:
	@echo "Starting backend (:8000) and frontend (:3000)…"
	@trap 'kill 0' INT TERM EXIT; \
	( cd backend && ../$(VENV)/bin/uvicorn app.main:app --reload --port 8000 ) & \
	( cd frontend && npm run dev ) & \
	wait

test:
	cd backend && ../$(VENV)/bin/python -m pytest -q

docker:
	docker compose up --build

clean:
	rm -rf $(VENV) frontend/node_modules frontend/.next backend/.cache
