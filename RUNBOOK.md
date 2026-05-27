# TaskFlow Runbook

## Local service startup

1. Start Docker Desktop.
2. Run `make compose-up`.
3. Check `docker compose ps`.
4. Open `http://localhost:8080`.

## Health checks

- Backend health: `curl http://localhost:8000/health`
- Backend metrics: `curl http://localhost:8000/metrics`
- Compose status: `docker compose ps`

## Common incidents

### Worker is restarting

1. Run `docker compose logs worker --tail=100`.
2. Confirm Redis connectivity.
3. Rebuild only the worker if code changed:
   - `docker compose up --build -d worker`

### Helm install fails policy or manifest validation

1. Run `make helm-lint`.
2. Run `make kube-render`.
3. Run `make policy-test`.
4. Fix the failing manifest before retrying deployment.

### Namespace is missing Pod Security labels

Run:

```bash
make namespace-labels
```

### Kubernetes debugging

- `kubectl get pods -n taskflow-dev`
- `kubectl describe pod <pod-name> -n taskflow-dev`
- `kubectl logs deployment/backend -n taskflow-dev`
- `kubectl logs deployment/worker -n taskflow-dev`
