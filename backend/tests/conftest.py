import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.cache import reset_redis_state
from app.config import reset_settings_state
from app.db import Base, get_engine, reset_database_state
from app.main import app


def configure_runtime(database_url: str, redis_url: str = "redis://localhost:6379/15") -> None:
    os.environ["TASKFLOW_DATABASE_URL"] = database_url
    os.environ["TASKFLOW_REDIS_URL"] = redis_url
    os.environ["TASKFLOW_SECRET_KEY"] = "test-secret"
    reset_settings_state()
    reset_database_state()
    reset_redis_state()


def reset_schema() -> None:
    engine = get_engine()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


@pytest.fixture
def sqlite_database_url(tmp_path) -> str:
    return f"sqlite:///{tmp_path / 'taskflow-test.db'}"


@pytest.fixture
def configured_sqlite(sqlite_database_url: str) -> str:
    configure_runtime(sqlite_database_url)
    reset_schema()
    yield sqlite_database_url
    reset_database_state()
    reset_redis_state()
    reset_settings_state()


@pytest.fixture
def client(configured_sqlite: str):
    with TestClient(app) as test_client:
        yield test_client
