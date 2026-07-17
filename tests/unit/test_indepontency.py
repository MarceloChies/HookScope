from app.services.idempotency import create_payload_fingerprint


def test_same_payload_with_different_key_order_has_same_fingerprint():
    first_payload = {
        "event": "payment.completed",
        "data": {"id": "payment_123"},
    }

    second_payload = {
        "data": {"id": "payment_123"},
        "event": "payment.completed",
    }

    assert create_payload_fingerprint(first_payload) == create_payload_fingerprint(second_payload)


def test_different_payloads_have_different_fingerprints():
    first_payload = {"event": "payment.completed"}
    second_payload = {"event": "payment.failed"}

    assert create_payload_fingerprint(first_payload) != create_payload_fingerprint(second_payload)