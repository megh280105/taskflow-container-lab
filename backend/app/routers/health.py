from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.cache import get_redis
from app.db import get_db

router = APIRouter()


@router.get("/health")
def healthcheck(db: Session = Depends(get_db)) -> dict[str, str]:
    db.execute(text("SELECT 1"))
    get_redis().ping()
    return {"status": "ok"}
