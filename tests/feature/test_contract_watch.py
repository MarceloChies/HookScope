from fastapi.testclient import TestClient


def test_webhook_with_wrong_contract_is_saved_with_issues(client: TestClient):
    endpoint_response = client.post(
        "/endpoints",
        json={
            "name": "Contract test endpoint",
            "destination_url": None,
        },
    )
    endpoint = endpoint_response.json()

    baseline = {
        "event": "payment.completed",
        "data": {
            "id": "payment_123",
            "amount": 100,
        },
    }

    contract_response = client.put(
        f"/endpoints/{endpoint['id']}/contract",
        json={"contract_baseline": baseline},
    )

    assert contract_response.status_code == 200

    webhook_response = client.post(
        f"/hooks/{endpoint['token']}",
        json={
            "event": "payment.completed",
            "data": {
                "id": 123,
            },
        },
    )

    assert webhook_response.status_code == 202

    delivery_response = client.get(
        f"/deliveries/{webhook_response.json()['delivery_id']}",
    )
    delivery = delivery_response.json()

    assert delivery["contract_valid"] is False
    assert len(delivery["contract_issues"]) == 2