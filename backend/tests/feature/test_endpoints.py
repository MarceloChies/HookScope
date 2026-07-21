import uuid

from fastapi.testclient import TestClient

from tests.feature.helpers import create_saved_delivery


def test_user_can_get_created_endpoint(client: TestClient):
    _, _, endpoint = create_saved_delivery(client)

    response = client.get(f"/endpoints/{endpoint['id']}")

    assert response.status_code == 200
    assert response.json() == endpoint


def test_unknown_endpoint_returns_404(client: TestClient):
    response = client.get(f"/endpoints/{uuid.uuid4()}")

    assert response.status_code == 404


def test_user_can_update_endpoint(client: TestClient):
    _, _, endpoint = create_saved_delivery(client)

    response = client.patch(
        f"/endpoints/{endpoint['id']}",
        json={
            "name": "Updated endpoint",
            "destination_url": "https://example.com/webhooks",
        },
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Updated endpoint"
    assert response.json()["destination_url"] == "https://example.com/webhooks"


def test_user_can_delete_endpoint(client: TestClient):
    _, _, endpoint = create_saved_delivery(client)

    delete_response = client.delete(f"/endpoints/{endpoint['id']}")
    get_response = client.get(f"/endpoints/{endpoint['id']}")

    assert delete_response.status_code == 204
    assert get_response.status_code == 404


def test_deleting_unknown_endpoint_returns_404(client: TestClient):
    response = client.delete(f"/endpoints/{uuid.uuid4()}")

    assert response.status_code == 404

def test_endpoint_stats_count_received_delivery(client: TestClient):
    _, _, endpoint = create_saved_delivery(client)

    response = client.get(
        f"/endpoints/{endpoint['id']}/stats"
    )
    assert response.status_code == 200

    stats = response.json()

    assert stats["total_deliveries"] == 1
    assert stats["total_attempts"] == 0
    assert stats["last_received_at"] is not None