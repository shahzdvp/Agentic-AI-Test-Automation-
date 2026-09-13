from httpx import Client


def test_get_nonexistent_item(api_client: Client):
    response = api_client.get("/api/v1/items/fake-id")
    assert response.status_code == 404

def test_update_nonexistent_item(api_client: Client):
    response = api_client.put("/api/v1/items/fake-id", json={"title": "New Title"})
    assert response.status_code == 404

def test_delete_nonexistent_item(api_client: Client):
    response = api_client.delete("/api/v1/items/fake-id")
    assert response.status_code == 404

def test_access_without_token(unauthenticated_client: Client):
    response = unauthenticated_client.get("/api/v1/items")
    assert response.status_code in (401, 403)

def test_access_with_invalid_token(unauthenticated_client: Client):
    response = unauthenticated_client.get(
        "/api/v1/items",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401
