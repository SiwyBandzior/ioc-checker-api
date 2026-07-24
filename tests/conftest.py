import os
from pathlib import Path

os.environ.setdefault("ABUSEIPDB_API_KEY", "test-key-for-tests")
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"

import pytest
from fastapi.testclient import TestClient

from main import app

TEST_DB = Path("test.db")


@pytest.fixture
def client():
    """Kazdy test dostaje swiezo utworzona, pusta baze testowa."""
    TEST_DB.unlink(missing_ok=True)

    with TestClient(app) as test_client:
        yield test_client

    TEST_DB.unlink(missing_ok=True)
