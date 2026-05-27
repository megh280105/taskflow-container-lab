# Docker, Containers & Kubernetes — Project Plan

A step-by-step roadmap to build a real, production-style application using Docker and Kubernetes. The goal isn't just "make it work" — it's to actually understand what you're doing at each stage.

---

## Project Idea

**Build a multi-service web application** — something realistic enough that containers and orchestration actually matter. A good choice:

> **"TaskFlow"** — a simple task/notes app with user authentication, a REST API, a database, a Redis cache, and a background worker (e.g. for sending reminder emails).

This gives you:
- A **frontend** (React, or even plain HTML)
- A **backend API** (Node.js / Python FastAPI / Go — pick what you know)
- A **PostgreSQL database** (stateful)
- A **Redis cache** (stateless, easy to scale)
- A **worker service** (background jobs)

That's 5 services — enough to learn networking, scaling, state, secrets, and orchestration properly.

---

## Prerequisites

Before starting, install:

- [ ] **Docker Desktop** (Win/Mac) or Docker Engine + Docker Compose (Linux)
- [ ] **kubectl** — the Kubernetes CLI
- [ ] **Minikube** or **kind** — local Kubernetes cluster
- [ ] **Helm** (install in Phase 5, not now)
- [ ] A code editor with YAML support (VS Code + Kubernetes extension is great)
- [ ] **Git** + a GitHub account

Verify with:
```bash
docker --version
kubectl version --client
minikube version
```

---

## Phase 1 — Build the App (no containers yet)

**Goal:** get a working app running locally without Docker, so containerization is the only new variable later.

- [ ] Set up the backend with a `/health`, `/tasks` (GET, POST), and `/login` endpoint
- [ ] Connect to a local PostgreSQL instance
- [ ] Connect to a local Redis instance
- [ ] Build the worker as a separate process that reads jobs from Redis
- [ ] Build a minimal frontend that calls the API
- [ ] **Use environment variables for all config** — never hardcode DB URLs, secrets, ports. This is critical for the next phases.

**Why this matters:** If your app reads config from env vars from day one, containerizing is painless. If it doesn't, you'll fight it the whole way.

---

## Phase 2 — Dockerize Each Service

**Goal:** every service runs in its own container.

- [ ] Write a `Dockerfile` for the backend
  - Use a specific base image tag (e.g. `node:20-alpine`), never `latest`
  - Use **multi-stage builds** to keep final images small
  - Run as a non-root user
  - Add a `.dockerignore` (exclude `node_modules`, `.git`, `.env`, etc.)
- [ ] Write a `Dockerfile` for the frontend (multi-stage: build → nginx serve)
- [ ] Write a `Dockerfile` for the worker
- [ ] Use **official images** for Postgres and Redis (don't build your own)
- [ ] Build each image: `docker build -t taskflow-api:0.1.0 .`
- [ ] Run each container manually with `docker run` to confirm it works
- [ ] Check image sizes with `docker images` — aim for backend < 200MB

**Concepts to learn here:** image layers, build cache, multi-stage builds, image tagging, the difference between `CMD` and `ENTRYPOINT`, why `COPY package.json` before `COPY .` matters for caching.

---

## Phase 3 — Orchestrate Locally with Docker Compose

**Goal:** spin up the entire stack with one command.

- [ ] Write a `docker-compose.yml` with all 5 services
- [ ] Define a custom network so services can talk by name (`postgres`, `redis`, etc.)
- [ ] Use **named volumes** for Postgres data so it survives restarts
- [ ] Use `depends_on` with health checks (not just service start order)
- [ ] Move secrets/config to a `.env` file (and add `.env` to `.gitignore`)
- [ ] Test: `docker compose up` should bring up everything; `docker compose down -v` should clean it up
- [ ] Verify scaling works: `docker compose up --scale worker=3`

**Milestone:** A new dev should be able to clone your repo, run one command, and have a working app.

---

## Phase 4 — Move to Kubernetes (the core learning phase)

**Goal:** translate everything from Compose to native Kubernetes manifests. Write YAML by hand — do *not* use a converter tool. The point is to learn.

### 4a. Set up a local cluster
- [ ] Start Minikube: `minikube start --cpus=4 --memory=4096`
- [ ] Verify: `kubectl get nodes`
- [ ] Enable the ingress addon: `minikube addons enable ingress`

### 4b. Core objects (build up in this order)
- [ ] **Namespace** — `taskflow-dev`, so your stuff is isolated
- [ ] **Deployments** for backend, frontend, worker (stateless)
- [ ] **Services** (ClusterIP) so pods can find each other by DNS
- [ ] **ConfigMaps** for non-secret config (log levels, feature flags)
- [ ] **Secrets** for DB passwords, API keys (base64-encoded, not encrypted — know the difference!)
- [ ] **StatefulSet** + **PersistentVolumeClaim** for Postgres
- [ ] **Deployment** for Redis (in-memory, but use a PVC if you want persistence)
- [ ] **Ingress** to route external traffic to frontend and `/api` to backend

### 4c. Make it production-ish
- [ ] **Liveness probes** — restart the pod if it's hung
- [ ] **Readiness probes** — don't send traffic until it's ready
- [ ] **Resource requests and limits** for every container (CPU + memory)
- [ ] **HorizontalPodAutoscaler** on the backend (e.g. scale on CPU > 70%)
- [ ] **PodDisruptionBudget** for high-availability services
- [ ] Use a **rolling update strategy** with `maxUnavailable` and `maxSurge`

### 4d. Things to verify
- [ ] Kill a pod with `kubectl delete pod ...` — it should come back
- [ ] Scale a deployment: `kubectl scale deployment backend --replicas=5`
- [ ] Roll out a new version: `kubectl set image deployment/backend api=taskflow-api:0.2.0`
- [ ] Roll back: `kubectl rollout undo deployment/backend`
- [ ] Watch logs: `kubectl logs -f deployment/backend`

**Concepts to learn here:** pods vs deployments, the Service abstraction, why DNS-based service discovery is so powerful, the StatefulSet vs Deployment difference, how secrets are mounted, how probes affect uptime.

---

## Phase 5 — Package with Helm

**Goal:** stop copy-pasting YAML for each environment.

- [ ] Install Helm
- [ ] Create a chart: `helm create taskflow`
- [ ] Move your manifests into the chart's `templates/` folder
- [ ] Templatize values: image tag, replica count, env, resource limits → all in `values.yaml`
- [ ] Create `values-dev.yaml` and `values-prod.yaml`
- [ ] Install: `helm install taskflow ./taskflow -f values-dev.yaml`
- [ ] Upgrade: `helm upgrade taskflow ./taskflow -f values-dev.yaml`
- [ ] Roll back: `helm rollback taskflow 1`

---

## Phase 6 — CI/CD Pipeline

**Goal:** push to `main` → image builds → deploys to cluster automatically.

- [ ] Push your code to GitHub
- [ ] Set up **GitHub Actions** workflow:
  - On pull request: lint, run tests, build image (don't push)
  - On merge to `main`: build image, tag with git SHA, push to a registry
- [ ] Use **Docker Hub** (free) or **GitHub Container Registry** (free for public)
- [ ] Add a deploy step: `helm upgrade --install` against your cluster
- [ ] (Bonus) Learn **GitOps** with Argo CD or Flux — much better than push-based deploys

---

## Phase 7 — Observability

**Goal:** know what's happening inside the cluster.

- [ ] Install **Prometheus** via the `kube-prometheus-stack` Helm chart
- [ ] Install **Grafana** (comes with the stack) and explore the default dashboards
- [ ] Add a `/metrics` endpoint to your backend (Prometheus format)
- [ ] Create a custom Grafana dashboard for your app's request rate and errors
- [ ] Install **Loki** for log aggregation
- [ ] Set up an alert (e.g. "fire when backend error rate > 5% for 5 minutes")

---

## Phase 8 — Deploy to a Real Cluster (Optional but recommended)

**Goal:** prove it works outside your laptop.

Options, cheapest first:
- **k3s on a cheap VPS** (~$5–10/month on Hetzner, DigitalOcean) — full control, very cheap
- **DigitalOcean Kubernetes** — managed, ~$12/month minimum
- **Google GKE Autopilot** — free control plane, pay per pod
- **AWS EKS** — most "industry standard" but most complex and expensive
- **Oracle Cloud Free Tier** — actually offers a free K8s cluster (with limits)

Don't forget to:
- [ ] Set up TLS with **cert-manager** + Let's Encrypt
- [ ] Buy a cheap domain ($10/yr on Namecheap or Porkbun)
- [ ] Configure DNS to point at your ingress
- [ ] **Tear it down when you're done** so you don't get a surprise bill

---

## Key Concepts Checklist

Things you should be able to explain in your own words by the end:

- [ ] Difference between a container and a VM
- [ ] What a container image actually is (layered filesystem + metadata)
- [ ] Why image tags like `latest` are a bad idea in production
- [ ] What `kubectl apply` actually does (declarative reconciliation)
- [ ] The control loop pattern — desired state vs actual state
- [ ] Why services exist (pods are ephemeral; their IPs change)
- [ ] When to use a Deployment vs StatefulSet vs DaemonSet vs Job
- [ ] How Kubernetes networking works (pod IP, ClusterIP, NodePort, LoadBalancer, Ingress)
- [ ] How rolling updates and rollbacks work under the hood
- [ ] What `kubectl get pod -o yaml` shows you and why it differs from what you applied

---

## Common Pitfalls to Avoid

- **Don't use `latest` tag** — pin to specific versions for reproducibility
- **Don't store secrets in Git** — even in private repos. Use Secrets + Sealed Secrets or external secret managers
- **Don't run as root** in containers — set a `USER` in your Dockerfile
- **Don't skip resource limits** — one runaway pod can take down a node
- **Don't put the database in a Deployment** — use a StatefulSet (or better, a managed DB)
- **Don't ignore `kubectl describe`** — it's the first thing to run when something's wrong
- **Don't jump to Helm/Kustomize too early** — write raw YAML first to actually learn

---

## Resources

**Official & free:**
- [Kubernetes Documentation](https://kubernetes.io/docs/home/) — genuinely excellent
- [Kubernetes Interactive Tutorials](https://kubernetes.io/docs/tutorials/) — hands-on basics
- [Play with Kubernetes](https://labs.play-with-k8s.com/) — browser-based cluster

**Deep dives:**
- *Kubernetes the Hard Way* by Kelsey Hightower (GitHub) — build a cluster from scratch
- *Kubernetes Up & Running* (book) — solid foundation
- [KubeAcademy](https://kube.academy/) — free video courses

**Tools to know later:**
- **k9s** — terminal UI for kubectl, makes life much easier
- **Lens / Headlamp** — desktop GUI for clusters
- **Stern** — multi-pod log tailing
- **kubectx / kubens** — switch contexts and namespaces fast

---

## Suggested Timeline

| Phase | Time commitment |
|-------|-----------------|
| Phase 1 — Build the app | 1 weekend |
| Phase 2 — Dockerize | 2–3 evenings |
| Phase 3 — Compose | 1 evening |
| Phase 4 — Kubernetes core | 1–2 weekends |
| Phase 5 — Helm | 1 evening |
| Phase 6 — CI/CD | 1 weekend |
| Phase 7 — Observability | 1 weekend |
| Phase 8 — Real cluster | 1 weekend |

**Total: roughly 4–6 weeks** of part-time effort to go from zero to a real cloud-deployed app you actually understand.

---

## Definition of Done

You'll know you're done when:

1. A teammate can clone your repo and `helm install` your app on their cluster in under 5 minutes.
2. You can deploy a new version with zero downtime.
3. If a pod crashes, you can find out why within 60 seconds using your logs/metrics.
4. You can explain every line of your manifests without looking at the docs.

Good luck — and remember: **break things on purpose.** Kill pods, fill up disks, crash the database. Kubernetes is most educational when it's recovering from disasters you caused.
