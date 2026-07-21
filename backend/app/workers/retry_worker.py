import asyncio
from datetime import datetime, timezone

from sqlalchemy import select

from app.database.models.delivery import Delivery
from app.database.models.endpoint import WebhookEndpoint
from app.database.session import SessionLocal
from app.services.forwarding import forward_delivery

async def process_due_retries() -> int:
    now = datetime.now(timezone.utc)

    with SessionLocal() as db:
        due_deliveries = db.scalars(
            select(Delivery).where(
                Delivery.next_retry_at.is_not(None),
                Delivery.next_retry_at <= now,
            )
        ).all()

        retried_count = 0

        for delivery in due_deliveries:
            endpoint = db.get(
                WebhookEndpoint,
                delivery.endpoint_id,
            )

            if endpoint is None or endpoint.destination_url is None:
                delivery.next_retry_at = None
                db.commit()
                continue

            await forward_delivery(
                delivery=delivery,
                destination_url=endpoint.destination_url,
                db=db,
            )
            retried_count += 1

        return retried_count
    
def main() -> None:
    retried_count = asyncio.run(process_due_retries())
    print(f"Retried {retried_count} deliveries.")

if __name__ == "__main__":
    main()