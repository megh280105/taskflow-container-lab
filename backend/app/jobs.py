import logging
from datetime import datetime, timezone

from rq import Queue
from sqlalchemy import select

from app.cache import get_redis
from app.db import SessionLocal
from app.models import Task

logger = logging.getLogger(__name__)
QUEUE_NAME = "taskflow-reminders"


def get_queue() -> Queue:
    return Queue(QUEUE_NAME, connection=get_redis())


def enqueue_task_reminder(task_id: int) -> None:
    queue = get_queue()
    queue.enqueue("app.jobs.send_task_reminder", task_id, job_timeout=300)


def send_task_reminder(task_id: int) -> None:
    with SessionLocal() as db:
        task = db.scalar(select(Task).where(Task.id == task_id))
        if task is None:
            logger.warning("Reminder skipped because task %s was not found", task_id)
            return

        logger.info(
            "Simulated reminder email",
            extra={
                "task_id": task.id,
                "title": task.title,
                "owner_id": task.owner_id,
                "due_at": task.due_at.isoformat() if task.due_at else None,
            },
        )
        task.reminder_sent_at = datetime.now(timezone.utc)
        db.add(task)
        db.commit()
