from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.deps import get_current_user
from app.db import get_db
from app.jobs import enqueue_task_reminder
from app.models import Task, User
from app.schemas import TaskCreate, TaskRead, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=list[TaskRead])
def list_tasks(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[Task]:
    statement = select(Task).where(Task.owner_id == current_user.id).order_by(Task.created_at.desc())
    return list(db.scalars(statement))


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(
    payload: TaskCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> Task:
    task = Task(
        title=payload.title.strip(),
        description=payload.description,
        due_at=payload.due_at,
        owner_id=current_user.id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    if payload.due_at is not None and payload.due_at > datetime.now(timezone.utc):
        enqueue_task_reminder(task.id)

    return task


@router.patch("/{task_id}", response_model=TaskRead)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Task:
    task = db.scalar(select(Task).where(Task.id == task_id, Task.owner_id == current_user.id))
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    changes = payload.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(task, field, value)

    if "due_at" in changes:
        task.reminder_sent_at = None
        if task.due_at is not None and task.due_at > datetime.now(timezone.utc):
            enqueue_task_reminder(task.id)

    db.add(task)
    db.commit()
    db.refresh(task)
    return task
