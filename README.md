# TaskFlow

TaskFlow is a small production-style learning project built from the roadmap in `plan.md`. It includes a FastAPI API, a React frontend, PostgreSQL for persistence, Redis for caching and job queues, and a worker that processes reminder jobs.

## Stack

- Backend: FastAPI + SQLAlchemy
- Frontend: React + Vite
- Database: PostgreSQL
- Cache / queue: Redis
- Worker: Python + RQ
- Container orchestration: Docker Compose, Kubernetes, Helm

## Core flows

- Users register and log in with email/password.
- Authenticated users can create and list their tasks.
- Tasks can include a due date.
- Creating a task with a due date enqueues a reminder job in Redis.
- The worker consumes the queue and simulates sending a reminder.

## Important files

- `backend/` holds the API, worker, and tests.
- `frontend/` holds the React application.
- `infra/k8s/base/` holds raw Kubernetes manifests.
- `infra/helm/taskflow/` holds the Helm chart.
- `policy/` holds Kubernetes policy checks used in CI.
- `Makefile` holds the common local dev and validation commands.
- `tracker.md` shows current implementation status.

## v2 foundation

The repo now includes the first v2 hardening slice:

- Backend coverage gate and richer API/job/worker tests
- Optional container-backed integration test with real Postgres and Redis
- Kubernetes ServiceAccounts, NetworkPolicies, and stricter pod/container security defaults
- Helm, Kustomize, and policy validation paths for CI
- Supporting docs in `ARCHITECTURE.md`, `CONTRIBUTING.md`, and `RUNBOOK.md`

## Run locally with Docker Compose

1. Start Docker Desktop or another local Docker daemon.
2. From the project root, copy `.env.example` if you want custom values:
   - `cp .env.example .env`
3. Build and start the stack:
   - `docker compose up --build`
4. Open the apps:
   - Frontend: `http://localhost:8080`
   - Backend API: `http://localhost:8000`
   - Backend health: `http://localhost:8000/health`
   - Backend metrics: `http://localhost:8000/metrics`
5. Stop everything:
   - `docker compose down`

## Validation commands

- `make test`
- `make frontend-build`
- `make helm-lint`
- `make kube-render`
- `make policy-test`

## Run the backend without Docker

1. Create a virtual environment:
   - `python3 -m venv .venv`
2. Install backend dependencies:
   - `.venv/bin/pip install -e './backend[dev]'`
3. Start Postgres and Redis locally or point the env vars at existing instances.
4. Run the API:
   - `.venv/bin/uvicorn app.main:app --app-dir backend --reload --host 0.0.0.0 --port 8000`
5. Run the worker in another terminal:
   - `.venv/bin/python backend/worker.py`

## Run the frontend without Docker

1. Install dependencies:
   - `cd frontend && npm install`
2. Start the dev server:
   - `npm run dev`
3. Open `http://localhost:5173`
