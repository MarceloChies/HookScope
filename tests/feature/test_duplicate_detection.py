from fastapi.testclient import TestClient

from tests.feature.helpers import create_saved_delivery


def test_identical_payloads_are_not_flagged_when_detection_is_disabled(
    client: TestClient,
):
    _, payload, endpoint = create_saved_delivery(client)

    response = client.post(
        f"/hooks/{endpoint['token']}",
        json=payload,
    )

    assert response.status_code == 202
    assert response.json()["duplicate"] is False
    assert response.json()["duplicate_of_id"] is None


def test_second_identical_payload_links_to_first_delivery(
    client: TestClient,
):
    endpoint_response = client.post(
        "/endpoints",
        json={
            "name": "Duplicate Detection Test",
            "destination_url": None,
            "duplicate_detection_enabled": True,
        },
    )
    assert endpoint_response.status_code == 201

    endpoint = endpoint_response.json()
    payload = {"event": "payment.completed", "id": "evt_123"}

    first_response = client.post(f"/hooks/{endpoint['token']}", json=payload)
    second_response = client.post(f"/hooks/{endpoint['token']}", json=payload)

    assert first_response.status_code == 202
    assert second_response.status_code == 202
    assert second_response.json()["duplicate"] is True
    assert second_response.json()["duplicate_of_id"] == first_response.json()["delivery_id"]