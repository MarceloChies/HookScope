import asyncio
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

import app.workers.retry_worker as retry_worker

from app.database.models.delivery import Delivery
from app.database.models.endpoint import WebhookEndpoint

def test_worker_retries_due_delivery(
    db_session: Session,
    monkeypatch,
):
    endpoint = WebhookEndpoint(
        name="Retry test endpoint",
        token="retry-test-token",
        destination_url="https://example.com/webhooks",
    )

    delivery = Delivery(
        endpoint=endpoint,
        method="POST",
        headers={},
        payload={"event": "retry.test"},
        next_retry_at=datetime.now(timezone.utc) - timedelta(seconds=1),
    )

    db_session.add(delivery)
    db_session.commit()
    delivery_id = delivery.id

    forwarded_delivery_ids = []

    async def fake_forward_delivery(*, delivery, destination_url, db):
        forwarded_delivery_ids.append(delivery.id)
        delivery.next_retry_at = None
        db.commit()

    monkeypatch.setattr(
        retry_worker,
        "SessionLocal",
        lambda: db_session,
    )
    monkeypatch.setattr(
        retry_worker,
        "forward_delivery",
        fake_forward_delivery,
    )

    retried_count = asyncio.run(
        retry_worker.process_due_retries(),
    )

    assert retried_count == 1
    assert forwarded_delivery_ids == [delivery_id]