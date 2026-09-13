import pytest
from httpx import Client


def test_create_item(api_client: Client):
    response = api_client.post(
        "/api/v1/items",
        json={"title": "Test Item", "price": 10.5}
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["title"] == "Test Item"
    assert data["price"] == 10.5

def test_list_items_empty(api_client: Client):
    response = api_client.get("/api/v1/items")
    assert response.status_code == 200
    assert response.json() == []

def test_list_items_after_create(api_client: Client):
    api_client.post("/api/v1/items", json={"title": "Item 1", "price": 10.0})
    response = api_client.get("/api/v1/items")
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_get_item(api_client: Client):
    create_resp = api_client.post("/api/v1/items", json={"title": "Item 1", "price": 10.0})
    item_id = create_resp.json()["id"]

    get_resp = api_client.get(f"/api/v1/items/{item_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["title"] == "Item 1"

def test_update_item(api_client: Client):
    create_resp = api_client.post("/api/v1/items", json={"title": "Item 1", "price": 10.0})
    item_id = create_resp.json()["id"]

    update_resp = api_client.put(f"/api/v1/items/{item_id}", json={"title": "Updated Item"})
    assert update_resp.status_code == 200
    assert update_resp.json()["title"] == "Updated Item"
    assert update_resp.json()["price"] == 10.0

def test_delete_item(api_client: Client):
    create_resp = api_client.post("/api/v1/items", json={"title": "Item 1", "price": 10.0})
    item_id = create_resp.json()["id"]

    del_resp = api_client.delete(f"/api/v1/items/{item_id}")
    assert del_resp.status_code == 204

    get_resp = api_client.get(f"/api/v1/items/{item_id}")
    assert get_resp.status_code == 404

def test_create_item_full_lifecycle(api_client: Client):
    # Create
    create_resp = api_client.post("/api/v1/items", json={"title": "Lifecycle Item", "price": 99.99})
    assert create_resp.status_code == 201
    item_id = create_resp.json()["id"]

    # Read
    read_resp = api_client.get(f"/api/v1/items/{item_id}")
    assert read_resp.status_code == 200

    # Update
    update_resp = api_client.put(f"/api/v1/items/{item_id}", json={"price": 89.99})
    assert update_resp.status_code == 200

    # Delete
    del_resp = api_client.delete(f"/api/v1/items/{item_id}")
    assert del_resp.status_code == 204

@pytest.mark.parametrize(
    "invalid_payload, expected_status",
    [
        ({"title": "", "price": 10.0}, 422),
        ({"title": "Valid", "price": -5.0}, 422),
        ({"title": "Missing Price"}, 422),
    ]
)
def test_create_item_validation(api_client: Client, invalid_payload: dict, expected_status: int):
    response = api_client.post("/api/v1/items", json=invalid_payload)
    assert response.status_code == expected_status
