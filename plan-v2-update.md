# Project Plan — v2 Update

Follow-up to `plan.md`. This isn't a replacement — it's the **next layer** to add once you've finished (or are comfortably past) Phase 5 of the original plan. The goal of v2 is to go from "I built a working K8s app" to "I built something that looks like a real production system."

---

## Why a v2?

After finishing the original plan, you'll have a deployable, scalable app. But you'll also notice gaps that real production systems care about:

- Security was mentioned but not enforced
- Testing wasn't really covered
- Service-to-service traffic is unencrypted
- You have one environment, not a real dev → staging → prod flow
- No disaster recovery story
- You can deploy, but can't easily debug or experiment safely

v2 fixes all of that.

---

## Phase 9 — Security Hardening

**Goal:** make the cluster and app actually defensible, not just functional.

### Container & image security
- [ ] Scan images for vulnerabilities with **Trivy** or **Grype** in CI
- [ ] Fail the build if HIGH/CRITICAL CVEs are found
- [ ] Use **distroless** or **chainguard** base images for production
- [ ] Sign images with **cosign** (Sigstore) and verify signatures at deploy time
- [ ] Pin images by **digest** (`@sha256:...`), not just tag, for production

### Kubernetes security
- [ ] Enable **Pod Security Standards** (`restricted` profile) on your namespace
- [ ] Set `runAsNonRoot: true`, `readOnlyRootFilesystem: true`, drop all capabilities
- [ ] Define **NetworkPolicies** — default-deny, then explicitly allow needed traffic
- [ ] Set up **RBAC** properly — no `cluster-admin` for app service accounts
- [ ] Use **dedicated ServiceAccounts** per workload, not the `default` one
- [ ] Install **Falco** or **Tetragon** for runtime threat detection

### Secret management
- [ ] Replace plain K8s Secrets with **Sealed Secrets**, **External Secrets Operator**, or **Vault**
- [ ] Rotate database credentials automatically
- [ ] Never log secrets — audit your logging code

**Concepts to learn:** the difference between authentication and authorization in K8s, why namespaces aren't a security boundary by default, the principle of least privilege applied to pods.

---

## Phase 10 — Multi-Environment Setup

**Goal:** dev, staging, and production environments that don't step on each other.

- [ ] Create three namespaces (or three clusters, if you're ambitious): `dev`, `staging`, `prod`
- [ ] Use Helm `values-dev.yaml`, `values-staging.yaml`, `values-prod.yaml` to parametrize
- [ ] Or switch to **Kustomize** with `base/` + `overlays/dev|staging|prod` — try both, pick what you like
- [ ] Set up **branch-based deploys**: PR previews → dev, `main` → staging, tags → prod
- [ ] Add a manual approval gate before prod deploys in GitHub Actions
- [ ] Use different resource limits per environment (prod gets more, dev gets less)
- [ ] Use separate databases per environment (never share a DB across envs)

---

## Phase 11 — Service Mesh (Istio or Linkerd)

**Goal:** observable, secure service-to-service traffic without changing app code.

- [ ] Install **Linkerd** (easier to start with than Istio)
- [ ] Inject the sidecar proxy into your workloads
- [ ] Get free **mTLS** between all services
- [ ] Use the mesh's dashboard to see live traffic, latency, and success rate per service
- [ ] Try **traffic splitting**: send 10% of traffic to a new version
- [ ] Set up **retry policies** and **timeouts** at the mesh layer
- [ ] Optional: try Istio later when you want fine-grained traffic rules

**Note:** Service mesh is genuinely useful but also genuinely complex. Don't add it just because it's trendy. Add it when you have ≥3 services and need to answer "why is this slow?" or "is this traffic encrypted?"

---

## Phase 12 — Progressive Delivery

**Goal:** ship without fear.

- [ ] Install **Argo Rollouts** or **Flagger**
- [ ] Convert your Deployments to Rollouts
- [ ] Implement a **canary deploy**: 10% → 25% → 50% → 100% with pauses
- [ ] Add **automated rollback** based on metrics (error rate, latency)
- [ ] Try a **blue/green deployment** for the frontend
- [ ] Build a **feature flag** system (or use LaunchDarkly / Unleash) to decouple deploy from release

This is where deploys stop being scary.

---

## Phase 13 — GitOps with Argo CD

**Goal:** the cluster reflects what's in Git, automatically. No more `kubectl apply` by hand.

- [ ] Install **Argo CD**
- [ ] Move your Helm/Kustomize manifests to a separate `infra/` repo (or folder)
- [ ] Set up an Argo `Application` pointing at that repo
- [ ] Every Git commit to the infra repo = automatic sync to the cluster
- [ ] Set up **Argo CD Image Updater** so new images auto-deploy
- [ ] Enable **drift detection** — Argo will warn (or fix) if someone changes things in the cluster directly
- [ ] Add Slack/Discord notifications for sync events

**Why this matters:** GitOps gives you a real audit trail, easy rollbacks (just revert the commit), and disaster recovery (re-point Argo at a fresh cluster and you're back).

---

## Phase 14 — Testing Strategy

**Goal:** stop finding bugs in production.

### App-level
- [ ] Unit tests with > 70% coverage on the backend
- [ ] Integration tests against a real Postgres/Redis (use **testcontainers**)
- [ ] Contract tests between frontend and API
- [ ] End-to-end tests with **Playwright** or **Cypress**

### Infrastructure-level
- [ ] Lint manifests with **kubeval** or **kubeconform**
- [ ] Policy tests with **OPA / Conftest** ("no container can run as root", etc.)
- [ ] Lint Helm charts with `helm lint` and `helm template | kubectl apply --dry-run`
- [ ] Run your CI pipeline against a **kind** cluster — actually deploy in CI and run smoke tests
- [ ] Add **chaos tests** with **Litmus** or **Chaos Mesh** — randomly kill pods, simulate network failure, drain nodes

---

## Phase 15 — Backup & Disaster Recovery

**Goal:** be able to recover when (not if) things go wrong.

- [ ] Install **Velero** to back up cluster state and persistent volumes
- [ ] Schedule daily backups to S3-compatible storage (e.g. Backblaze B2, cheap)
- [ ] **Actually test a restore** — write down the steps, time yourself, fix what's broken
- [ ] Document your **RTO** (recovery time objective) and **RPO** (recovery point objective)
- [ ] For the database: set up **point-in-time recovery** (WAL archiving for Postgres)
- [ ] Write a runbook: "what to do if the cluster is gone"
- [ ] Do a **game day** — destroy the cluster on purpose, recover from backups, time the whole thing

This is the phase most people skip and regret.

---

## Phase 16 — Cost Optimization & Multi-Tenancy

**Goal:** stop overspending and start sharing infrastructure properly.

- [ ] Install **Kubecost** or **OpenCost** to see what each workload actually costs
- [ ] Right-size your resource requests based on **VPA (Vertical Pod Autoscaler)** recommendations
- [ ] Use **spot/preemptible nodes** for non-critical workloads
- [ ] Set up **cluster autoscaling** so nodes scale with demand
- [ ] Use **PriorityClasses** to evict low-priority workloads under pressure
- [ ] Implement **ResourceQuotas** and **LimitRanges** per namespace
- [ ] Set up **multi-tenancy** with vcluster or proper namespace isolation if you're sharing the cluster

---

## Phase 17 — Advanced Observability

**Goal:** know not just *what* is broken, but *why*.

- [ ] Add **distributed tracing** with **OpenTelemetry** + **Tempo** or **Jaeger**
- [ ] Instrument the backend so every request has a trace ID through all services
- [ ] Build a **Service Level Objective (SLO)** dashboard — "99.9% of requests under 200ms"
- [ ] Set up **error tracking** with **Sentry** or **GlitchTip** (self-hosted)
- [ ] Implement **structured logging** (JSON) everywhere
- [ ] Set up alert routing through **Alertmanager** → Slack/PagerDuty/email
- [ ] Tune alerts — kill anything that fires more than once a week without action

---

## Phase 18 — Documentation & Developer Experience

**Goal:** future-you (and any teammate) can be productive in an hour, not a week.

- [ ] Write an honest `README.md` — "what is this and how do I run it"
- [ ] Write an `ARCHITECTURE.md` with a diagram (use Excalidraw or Mermaid)
- [ ] Write a `RUNBOOK.md` — "if X breaks, do Y"
- [ ] Document every environment variable
- [ ] Create a `CONTRIBUTING.md` with the dev setup steps
- [ ] Set up **Tilt** or **Skaffold** for fast local dev loops against K8s
- [ ] Add a `Makefile` or `Taskfile` so common operations are one command

---

## Stretch Goals (pick what excites you)

- **Multi-cluster setup** — run across two regions with **Submariner** or **Cilium Cluster Mesh**
- **Custom Kubernetes Operator** — build your own controller for `TaskFlowBackup` or similar
- **Build a CRD** to extend the K8s API for your app
- **Migrate to eBPF networking** with Cilium and explore Hubble
- **Try WebAssembly workloads** in K8s with **SpinKube** or **wasmCloud**
- **AI-ops experiment** — feed Prometheus metrics into an LLM for anomaly explanation

---

## Suggested Timeline

| Phase | Time |
|-------|------|
| Phase 9 — Security | 1 weekend |
| Phase 10 — Multi-env | 2–3 evenings |
| Phase 11 — Service mesh | 1 weekend |
| Phase 12 — Progressive delivery | 1 weekend |
| Phase 13 — GitOps | 1 weekend |
| Phase 14 — Testing | 1–2 weekends |
| Phase 15 — Backup & DR | 1 weekend |
| Phase 16 — Cost optimization | 2–3 evenings |
| Phase 17 — Advanced observability | 1 weekend |
| Phase 18 — Docs & DX | spread across the others |

**Total: roughly 6–8 weeks** of part-time effort on top of the original plan.

---

## Priority Order (if you can't do it all)

If you only have time for a few of these, do them in this order:

1. **Phase 14 — Testing** (you'll thank yourself)
2. **Phase 13 — GitOps** (huge quality-of-life win)
3. **Phase 9 — Security** (don't ship insecure stuff publicly)
4. **Phase 15 — Backup & DR** (boring until you need it)
5. **Phase 17 — Observability** (debugging without it is misery)
6. **Phase 10 — Multi-env** (only if you're collaborating with others)
7. Everything else as you have appetite

---

## Updated Definition of Done

After v2, you should be able to say:

1. **Every deploy is automated and reversible.** No manual `kubectl apply`. Reverting a Git commit rolls back the change.
2. **You can lose the entire cluster** and be back up in under an hour from backups.
3. **A new vulnerability disclosure** doesn't panic you — your scanner already flagged it and a PR is open.
4. **You can answer "why is this slow?"** with a trace, not a guess.
5. **You can ship a risky change** behind a feature flag and a canary, and roll it back automatically if metrics dip.
6. **Onboarding a new contributor** takes one afternoon, not one week.

That's the difference between "I made a Kubernetes project" and "I built something I'd trust in production."
