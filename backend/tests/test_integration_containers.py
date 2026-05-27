import os
from pathlib import Path
from datetime import datetime, timedelta, timezone

import docker
import pytest
from fastapi.testclient import TestClient
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer

from app.jobs import get_queue, send_task_reminder
from app.main import app
from tests.conftest import configure_runtime, reset_schema


def normalize_postgres_url(database_url: str) -> str:
    if database_url.startswith("postgresql+psycopg://"):
        return database_url
    if database_url.startswith("postgresql+psycopg2://"):
        return database_url.replace("postgresql+psycopg2://", "postgresql+psycopg://", 1)
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return database_url


def test_app_flow_with_real_postgres_and_redis() -> None:
    docker_desktop_socket = Path.home() / ".docker/run/docker.sock"
    if "DOCKER_HOST" not in os.environ and docker_desktop_socket.exists():
        os.environ["DOCKER_HOST"] = f"unix://{docker_desktop_socket}"

    try:
        docker.from_env().ping()
    except Exception as exc:  # pragma: no cover - environment-specific skip
        pytest.skip(f"Docker socket is not reachable for testcontainers: {exc}")

    with PostgresContainer("postgres:16-alpine") as postgres, RedisContainer("redis:7-alpine") as redis:
        configure_runtime(
            database_url=normalize_postgres_url(postgres.get_connection_url()),
            redis_url=redis.get_connection_url(),
        )
        reset_schema()

        with TestClient(app) as client:
            client.post("/register", json={"email": "real@example.com", "password": "password123"})
            login_response = client.post("/login", json={"email": "real@example.com", "password": "password123"})
            token = login_response.json()["access_token"]

            due_at = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
            create_response = client.post(
                "/tasks",
                headers={"Authorization": f"Bearer {token}"},
                json={"title": "Container-backed task", "description": "real deps", "due_at": due_at},
            )
            assert create_response.status_code == 201
            task = create_response.json()

            assert get_queue().count == 1
            send_task_reminder(task["id"])

            list_response = client.get("/tasks", headers={"Authorization": f"Bearer {token}"})
            tasks = list_response.json()
            assert tasks[0]["title"] == "Container-backed task"
            assert tasks[0]["reminder_sent_at"] is not None
