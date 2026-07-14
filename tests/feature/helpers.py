from fastapi.testclient import TestClient


def create_saved_delivery(client: TestClient) -> tuple[str, dict, dict]:
    """Create an endpoint, send it a webhook, and return its saved data."""

    endpoint_response = client.post(
        "/endpoints",
        json={
            "name": "Test Endpoint",
            "destination_url": None,
        },
    )
    assert endpoint_response.status_code == 201

    endpoint = endpoint_response.json()
    payload = {"event": "payment.completed"}

    webhook_response = client.post(
        f"/hooks/{endpoint['token']}",
        json=payload,
        headers={"Cookie": "secret-session-value"},
    )
    assert webhook_response.status_code == 202

    return webhook_response.json()["delivery_id"], payload, endpoint
