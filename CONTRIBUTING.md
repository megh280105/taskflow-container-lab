# Contributing

## Local setup

1. Install Python 3.12+ and Node 22+.
2. Run `make install-backend`.
3. Run `make install-frontend`.
4. Start Docker Desktop if you want integration tests or Compose.

## Common commands

- `make test` runs the backend test suite.
- `make frontend-build` verifies the frontend production bundle.
- `make helm-lint` lints the Helm chart.
- `make kube-render` renders and client-validates Helm and raw Kubernetes YAML.
- `make policy-test` runs the Kubernetes policy checks with Conftest.
- `make compose-up` starts the local multi-service stack.

## Testing expectations

- Fast API tests should stay green on every change.
- Container-backed integration tests should pass in CI and on any machine with a reachable Docker socket.
- Changes to manifests or Helm templates should be validated with `make kube-render` and `make policy-test`.

## Pull request expectations

- Keep commits focused.
- Update docs when the developer workflow changes.
- Avoid committing `.env`, `.venv`, or generated artifacts.
