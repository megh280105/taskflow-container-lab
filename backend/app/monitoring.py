from time import perf_counter

from fastapi import Request, Response
from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter(
    "taskflow_http_requests_total",
    "Total HTTP requests handled by TaskFlow.",
    ["method", "path", "status_code"],
)
REQUEST_LATENCY = Histogram(
    "taskflow_http_request_duration_seconds",
    "TaskFlow request latency in seconds.",
    ["method", "path"],
)


async def record_metrics(request: Request, call_next) -> Response:
    started_at = perf_counter()
    response = await call_next(request)
    route = request.scope.get("route")
    path = getattr(route, "path", request.url.path)
    elapsed = perf_counter() - started_at

    REQUEST_COUNT.labels(request.method, path, str(response.status_code)).inc()
    REQUEST_LATENCY.labels(request.method, path).observe(elapsed)
    return response
