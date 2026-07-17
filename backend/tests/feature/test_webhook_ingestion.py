from fastapi.testclient import TestClient

from tests.feature.helpers import create_saved_delivery


def test_receiving_webhook_saves_delivery(client: TestClient):
    delivery_id, expected_payload, _ = create_saved_delivery(client)

    response = client.get(f"/deliveries/{delivery_id}")

    assert response.status_code == 200
    assert response.json()["payload"] == expected_payload


def test_unknown_webhook_token_returns_404(client: TestClient):
    response = client.post(
        "/hooks/not-a-real-token",
        json={"event": "test"},
    )

    assert response.status_code == 404
