from httpx import Client


def test_login_success(unauthenticated_client: Client):
    response = unauthenticated_client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "secretpassword"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_wrong_password(unauthenticated_client: Client):
    response = unauthenticated_client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "wrongpassword"}
    )
    assert response.status_code == 401

def test_login_wrong_username(unauthenticated_client: Client):
    response = unauthenticated_client.post(
        "/api/v1/auth/login",
        json={"username": "wronguser", "password": "secretpassword"}
    )
    assert response.status_code == 401

def test_login_missing_fields(unauthenticated_client: Client):
    response = unauthenticated_client.post("/api/v1/auth/login", json={})
    assert response.status_code == 422
