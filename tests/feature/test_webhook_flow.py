import uuid
from fastapi.testclient import TestClient

def create_saved_delivery(client: TestClient) -> tuple[str,dict, dict]:
    endpoint_response = client.post(
        "/endpoints",
        json={
            "name": "Test Endpoint",
            "destination_url": None,
        },
    )
    assert endpoint_response.status_code ==201

    token = endpoint_response.json()["token"]
    payload = {"event": "payment.completed"}

    webhook_response = client.post(
        f"/hooks/{token}",
        json=payload,
        headers={
            "Cookie": "secret-session-value",
        },
    )
    assert webhook_response.status_code == 202
    
    endpoint = endpoint_response.json()
    delivery_id = webhook_response.json()["delivery_id"]

    return delivery_id, payload, endpoint


def test_get_delivery_returns_saved_payload(client: TestClient):
    delivery_id, expected_payload, _ = create_saved_delivery(client)

    response = client.get(f"/deliveries/{delivery_id}")

    assert response.status_code == 200
    assert response.json()["id"] == delivery_id
    assert response.json()["payload"] == expected_payload


def test_user_can_create_endpoint_receive_webhook_and_list_delivery(client: TestClient):

    delivery_id, expected_payload, _ = create_saved_delivery(client)

    response = client.get("/deliveries")
    assert response.status_code == 200

    deliveries = response.json()
    assert len(deliveries) == 1
    delivery = deliveries[0]
    assert delivery["id"] == delivery_id

    assert delivery["payload"] == expected_payload
    assert delivery["headers"]["cookie"] == "[REDACTED]"

def test_unknown_webhook_token_returns_404(client: TestClient):
    response = client.post(
        "/hooks/not-a-real-token",
        json={"event": "test"},
    )

    assert response.status_code == 404

def test_get_unknown_delivery_reutnrs_404(client: TestClient):
    unknown_delivery_id = uuid.uuid4()
    response = client.get(f"/deliveries/{unknown_delivery_id}")
    assert response.status_code == 404

def test_retry_returns_404(client:TestClient):
    unknown_delivery_id = uuid.uuid4()
    response = client.post(
        f"/deliveries/{unknown_delivery_id}/retry"
    )
    assert response.status_code == 404

def test_returns_list_after_creating_an_endpoint(client: TestClient):
    _, _, endpoint = create_saved_delivery(client)
    endpoint_id = endpoint["id"]
    response = client.get(f"/endpoints/{endpoint_id}")
    assert response.status_code==200
    assert response.json() == endpoint

def test_return_404_with_unknown_id(client: TestClient):
    unknown_endpoint_id = uuid.uuid4()
    response = client.get(
        f"/endpoints/{unknown_endpoint_id}"
    )
    assert response.status_code == 404

def test_update_endpoint(client: TestClient):
    _,_, endpoint = create_saved_delivery(client)

    response = client.patch(
        f"/endpoints/{endpoint["id"]}",
        json={
            "name": "Updated endpoint",
            "destination_url": "Updated destination url"
        },
    )
    assert response.status_code ==200
    assert response.json()["name"] == "Updated endpoint"
    assert response.json()["destination_url"] == "Updated destination url"
