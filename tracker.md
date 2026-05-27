# Live Tracker

## Working On

- Preparing the first v2 hardening slice for push and server deployment

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
- Installed `helm` locally and rendered the chart successfully
- Started Docker Desktop and verified the Compose stack builds and starts
- Fixed the worker runtime crash caused by an outdated `rq` import
- Verified the backend health endpoint, frontend HTTP response, and live app UI in the in-app browser
- Expanded backend coverage with API, job, and worker tests plus a container-backed integration test path
- Added a backend coverage gate and testcontainer dependencies for CI
- Hardened raw Kubernetes manifests with Pod Security labels, ServiceAccounts, NetworkPolicies, and stricter security contexts
- Mirrored the security hardening into the Helm chart and added `values-staging.yaml`
- Added repo-level policy validation with Conftest plus manifest validation with kubeconform
- Added operator docs: `ARCHITECTURE.md`, `CONTRIBUTING.md`, `RUNBOOK.md`, and a `Makefile`
- Rebuilt the Docker Compose stack after the frontend moved to an unprivileged NGINX runtime

## Blocked / Needs Local Runtime

- No Kubernetes cluster is currently configured in this workspace, so live `helm install`/rollout verification is still pending

## Left

- Create or attach to a Kubernetes cluster
- Label the namespace and install the hardened Helm chart
- Add later-stage v2 items like GitOps, backup/restore, and progressive delivery
