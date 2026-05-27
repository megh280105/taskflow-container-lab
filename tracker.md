# Live Tracker

## Working On

- Runtime verification and environment blockers

## Done

- Picked concrete stack: FastAPI, React/Vite, PostgreSQL, Redis, Python worker
- Defined initial product scope: per-user tasks, JWT auth, Redis-backed reminder jobs
- Created repo structure for backend, frontend, Kubernetes, Helm, and CI
- Implemented backend API, worker queue integration, config loading, and metrics endpoint
- Added backend tests for auth helpers and the register/login/task flow
- Built the React frontend and connected it to the API
- Added backend, worker, and frontend Dockerfiles plus a full `docker-compose.yml`
- Added raw Kubernetes manifests with namespace, services, deployments, StatefulSet, ingress, HPA, and PDBs
- Added a Helm chart with dev/prod values
- Added GitHub Actions CI/CD workflow and observability scaffolding

## Blocked / Needs Local Runtime

- Docker Compose runtime verification is blocked because the local Docker daemon is not reachable
- Helm chart rendering is blocked because `helm` is not installed on this machine

## Left

- Start Docker locally and verify `docker compose up --build`
- Install Helm and render or install the chart
- Run live browser verification against the composed app
