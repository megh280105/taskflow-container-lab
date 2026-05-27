import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

os.environ["TASKFLOW_DATABASE_URL"] = f"sqlite:///{Path(__file__).parent / 'security-test.db'}"
os.environ["TASKFLOW_REDIS_URL"] = "redis://localhost:6379/15"
os.environ["TASKFLOW_SECRET_KEY"] = "test-secret"

from app.security import create_access_token, decode_token, hash_password, verify_password


def test_password_hash_round_trip() -> None:
    password = "super-secret-password"
    hashed = hash_password(password)

    assert password != hashed
    assert verify_password(password, hashed)


def test_token_round_trip() -> None:
    token = create_access_token("dev@example.com")
    assert decode_token(token) == "dev@example.com"
