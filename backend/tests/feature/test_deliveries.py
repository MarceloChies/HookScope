import uuid

from fastapi.testclient import TestClient

from tests.feature.helpers import create_saved_delivery


def test_list_deliveries_returns_saved_delivery(client: TestClient):
    delivery_id, expected_payload, _ = create_saved_delivery(client)

    response = client.get("/deliveries")

    assert response.status_code == 200
    assert response.json()[0]["id"] == delivery_id
    assert response.json()[0]["payload"] == expected_payload
    assert response.json()[0]["headers"]["cookie"] == "[REDACTED]"


def test_unknown_delivery_returns_404(client: TestClient):
    response = client.get(f"/deliveries/{uuid.uuid4()}")

    assert response.status_code == 404


def test_retrying_unknown_delivery_returns_404(client: TestClient):
    response = client.post(f"/deliveries/{uuid.uuid4()}/retry")

    assert response.status_code == 404


def test_user_can_filter_deliveries_by_endpoint(client: TestClient):
    first_delivery_id, _, first_endpoint = create_saved_delivery(client)
    create_saved_delivery(client)

    response = client.get(
        f"/deliveries?endpoint_id={first_endpoint['id']}",
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == first_delivery_id
