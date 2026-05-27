from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.jobs import send_task_reminder
from app.models import Task, User
from app.security import hash_password


def test_send_task_reminder_marks_task_as_sent(configured_sqlite) -> None:
    from app.db import get_session_local

    with get_session_local()() as db:
        user = User(email="queue@example.com", password_hash=hash_password("password123"))
        db.add(user)
        db.commit()
        db.refresh(user)

        task = Task(
            title="Reminder task",
            description="queue",
            owner_id=user.id,
            due_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        task_id = task.id

    send_task_reminder(task_id)

    with get_session_local()() as db:
        reloaded_task = db.scalar(select(Task).where(Task.id == task_id))
        assert reloaded_task is not None
        assert reloaded_task.reminder_sent_at is not None


def test_send_task_reminder_skips_missing_tasks(configured_sqlite, caplog) -> None:
    send_task_reminder(9999)
    assert "Reminder skipped because task 9999 was not found" in caplog.text
