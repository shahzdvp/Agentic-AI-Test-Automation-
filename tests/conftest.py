import sys
from pathlib import Path

import pytest
from httpx import Client

# Add src to path so imports work
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from fastapi.testclient import TestClient

from sample_app.main import ITEMS_DB, app


@pytest.fixture(scope="session")
def unauthenticated_client():
    client = TestClient(app)
    yield client

@pytest.fixture(scope="session")
def auth_token(unauthenticated_client: Client) -> str:
    response = unauthenticated_client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "secretpassword"}
    )
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest.fixture(scope="function")
def api_client(unauthenticated_client: Client, auth_token: str):
    unauthenticated_client.headers.update({"Authorization": f"Bearer {auth_token}"})
    yield unauthenticated_client
    unauthenticated_client.headers.pop("Authorization", None)

@pytest.fixture(scope="function", autouse=True)
def clear_db():
    """Clear the items DB between tests."""
    ITEMS_DB.clear()
    yield
