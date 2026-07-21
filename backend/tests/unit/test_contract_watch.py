from app.services.contract_watch import compare_payload_contract


def test_contract_reports_missing_nested_field():
    baseline = {
        "event": "payment.completed",
        "data": {
            "id": "payment_123",
            "amount": 100,
        },
    }

    payload = {
        "event": "payment.completed",
        "data": {
            "id": "payment_123",
        },
    }

    changes = compare_payload_contract(baseline, payload)

    assert changes == [
        {
            "kind": "missing_field",
            "path": "payload.data.amount",
            "expected": "number",
            "actual": "missing",
        }
    ]


def test_contract_reports_changed_field_type():
    baseline = {
        "data": {
            "amount": 100,
        }
    }

    payload = {
        "data": {
            "amount": "100",
        }
    }

    changes = compare_payload_contract(baseline, payload)

    assert changes == [
        {
            "kind": "type_changed",
            "path": "payload.data.amount",
            "expected": "number",
            "actual": "string",
        }
    ]


def test_contract_reports_added_field():
    baseline = {
        "event": "payment.completed",
    }

    payload = {
        "event": "payment.completed",
        "request_id": "request_123",
    }

    changes = compare_payload_contract(baseline, payload)

    assert changes == [
        {
            "kind": "added_field",
            "path": "payload.request_id",
            "expected": "missing",
            "actual": "string",
        }
    ]


def test_contract_accepts_matching_payload():
    baseline = {
        "event": "payment.completed",
        "data": {
            "amount": 100,
        },
    }

    payload = {
        "event": "payment.completed",
        "data": {
            "amount": 250,
        },
    }

    changes = compare_payload_contract(baseline, payload)

    assert changes == []