PYTHON := .venv/bin/python
PIP := .venv/bin/pip
PYTEST := .venv/bin/pytest
NPM := npm

.PHONY: install-backend install-frontend test test-unit test-integration frontend-build \
	helm-lint kube-render policy-test compose-config compose-up compose-down \
	namespace-labels

install-backend:
	python3 -m venv .venv
	$(PIP) install -e './backend[dev]'

install-frontend:
	cd frontend && $(NPM) install

test:
	$(PYTEST) backend/tests -q

test-unit:
	$(PYTEST) backend/tests -q -k "not integration"

test-integration:
	$(PYTEST) backend/tests/test_integration_containers.py -q

frontend-build:
	cd frontend && $(NPM) run build

helm-lint:
	helm lint ./infra/helm/taskflow -f ./infra/helm/taskflow/values-dev.yaml

kube-render:
	mkdir -p .tmp
	helm template taskflow ./infra/helm/taskflow -f ./infra/helm/taskflow/values-dev.yaml > .tmp/helm.yaml
	kubectl kustomize infra/k8s/base > .tmp/kustomize.yaml
	kubeconform -summary -ignore-missing-schemas .tmp/helm.yaml
	kubeconform -summary -ignore-missing-schemas .tmp/kustomize.yaml

policy-test:
	mkdir -p .tmp
	helm template taskflow ./infra/helm/taskflow -f ./infra/helm/taskflow/values-dev.yaml > .tmp/helm.yaml
	kubectl kustomize infra/k8s/base > .tmp/kustomize.yaml
	docker run --rm -v "$$PWD":/project -w /project openpolicyagent/conftest:v0.59.0 test .tmp/helm.yaml .tmp/kustomize.yaml --policy ./policy

compose-config:
	docker compose config >/tmp/taskflow-compose.yaml

compose-up:
	docker compose up --build -d

compose-down:
	docker compose down

namespace-labels:
	kubectl label namespace taskflow-dev \
	  pod-security.kubernetes.io/enforce=restricted \
	  pod-security.kubernetes.io/enforce-version=latest \
	  pod-security.kubernetes.io/audit=restricted \
	  pod-security.kubernetes.io/audit-version=latest \
	  pod-security.kubernetes.io/warn=restricted \
	  pod-security.kubernetes.io/warn-version=latest --overwrite
