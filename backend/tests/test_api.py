from datetime import datetime, timedelta, timezone


def register_and_login(client, email: str = "demo@example.com", password: str = "password123") -> str:
    register_response = client.post("/register", json={"email": email, "password": password})
    assert register_response.status_code == 201

    login_response = client.post("/login", json={"email": email, "password": password})
    assert login_response.status_code == 200
    return login_response.json()["access_token"]


def test_register_login_create_list_and_update_task(client, monkeypatch) -> None:
    queued_task_ids = []
    monkeypatch.setattr("app.routers.tasks.enqueue_task_reminder", queued_task_ids.append)
    token = register_and_login(client)

    due_at = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    create_response = client.post(
        "/tasks",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": " Ship Compose stack ",
            "description": "Validate the worker and queue path",
            "due_at": due_at,
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

    update_response = client.patch(
        f"/tasks/{created_task['id']}",
        headers={"Authorization": f"Bearer {token}"},
        json={"completed": True},
    )
    assert update_response.status_code == 200
    assert update_response.json()["completed"] is True


def test_register_duplicate_email_is_rejected(client) -> None:
    first_response = client.post("/register", json={"email": "demo@example.com", "password": "password123"})
    second_response = client.post("/register", json={"email": "demo@example.com", "password": "password123"})

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "Email already registered"


def test_login_with_invalid_password_is_rejected(client) -> None:
    client.post("/register", json={"email": "demo@example.com", "password": "password123"})
    login_response = client.post("/login", json={"email": "demo@example.com", "password": "wrong-pass-123"})

    assert login_response.status_code == 401
    assert login_response.json()["detail"] == "Invalid email or password"


def test_tasks_require_authentication(client) -> None:
    response = client.get("/tasks")
    assert response.status_code == 401


def test_user_cannot_update_another_users_task(client, monkeypatch) -> None:
    monkeypatch.setattr("app.routers.tasks.enqueue_task_reminder", lambda *_args: None)
    first_token = register_and_login(client, email="owner@example.com")
    second_token = register_and_login(client, email="other@example.com")

    create_response = client.post(
        "/tasks",
        headers={"Authorization": f"Bearer {first_token}"},
        json={"title": "Owner task", "description": "private"},
    )
    task_id = create_response.json()["id"]

    update_response = client.patch(
        f"/tasks/{task_id}",
        headers={"Authorization": f"Bearer {second_token}"},
        json={"completed": True},
    )

    assert update_response.status_code == 404
    assert update_response.json()["detail"] == "Task not found"


def test_health_and_metrics_endpoints_report_status(client, monkeypatch) -> None:
    class FakeRedis:
        def ping(self) -> bool:
            return True

    monkeypatch.setattr("app.routers.health.get_redis", lambda: FakeRedis())
    health_response = client.get("/health")
    assert health_response.status_code == 200
    assert health_response.json() == {"status": "ok"}

    metrics_response = client.get("/metrics")
    assert metrics_response.status_code == 200
    assert "taskflow_http_requests_total" in metrics_response.text
    assert "taskflow_http_request_duration_seconds" in metrics_response.text
