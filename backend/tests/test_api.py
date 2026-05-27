import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

os.environ["TASKFLOW_DATABASE_URL"] = f"sqlite:///{Path(__file__).parent / 'api-test.db'}"
os.environ["TASKFLOW_REDIS_URL"] = "redis://localhost:6379/15"
os.environ["TASKFLOW_SECRET_KEY"] = "test-secret"

from fastapi.testclient import TestClient

from app.db import Base, engine
from app.main import app


def reset_database() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_register_login_and_create_task(monkeypatch) -> None:
    reset_database()
    queued_task_ids = []
    monkeypatch.setattr("app.routers.tasks.enqueue_task_reminder", queued_task_ids.append)

    with TestClient(app) as client:
        register_response = client.post(
            "/register",
            json={"email": "demo@example.com", "password": "password123"},
        )
        assert register_response.status_code == 201

        login_response = client.post(
            "/login",
            json={"email": "demo@example.com", "password": "password123"},
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        create_response = client.post(
            "/tasks",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": "Ship Compose stack",
                "description": "Validate the worker and queue path",
                "due_at": "2099-01-01T10:00:00Z",
            },
        )
        assert create_response.status_code == 201
        created_task = create_response.json()
        assert created_task["title"] == "Ship Compose stack"
        assert queued_task_ids == [created_task["id"]]

        list_response = client.get("/tasks", headers={"Authorization": f"Bearer {token}"})
        assert list_response.status_code == 200
        tasks = list_response.json()
        assert len(tasks) == 1
        assert tasks[0]["title"] == "Ship Compose stack"
