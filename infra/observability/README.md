# Observability Notes

TaskFlow exposes Prometheus-format metrics at `/metrics` from the backend service. The Kubernetes manifests and Helm chart both include scrape hints, and the Helm chart optionally renders a `ServiceMonitor`.

## Suggested install flow

1. Install Prometheus and Grafana:
   - `helm repo add prometheus-community https://prometheus-community.github.io/helm-charts`
   - `helm upgrade --install monitoring prometheus-community/kube-prometheus-stack -n monitoring --create-namespace -f infra/observability/prometheus-values.yaml`
2. Install Loki:
   - `helm repo add grafana https://grafana.github.io/helm-charts`
   - `helm upgrade --install loki grafana/loki-stack -n monitoring -f infra/observability/loki-values.yaml`
3. Enable the chart `ServiceMonitor`:
   - `helm upgrade --install taskflow ./infra/helm/taskflow -n taskflow-dev --create-namespace -f ./infra/helm/taskflow/values-dev.yaml --set serviceMonitor.enabled=true`
4. Import `infra/observability/taskflow-dashboard.json` into Grafana.

## Dashboard focus

- Request rate per endpoint
- Error count by status code
- Request latency percentile
- Pod CPU and memory usage
- Worker and backend logs in Loki
