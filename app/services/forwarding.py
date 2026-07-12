import httpx
from sqlalchemy.orm import Session

from app.database.models.attempt import DeliveryAttempt
from app.database.models.delivery import Delivery

MAX_RESPONSE_LENGHT = 2000

async def forward_delivery(
        delivery:Delivery,
        destination_url: str,
        db:Session,
) -> DeliveryAttempt:
    attempt = DeliveryAttempt(
        delivery_id= delivery.id,
        attempt_number=1,
    )

    try:
        async with httpx.AsyncClient(
            timeout=10.0,
            follow_redirects=False,
        ) as client:
            response = await client.post(
                destination_url,
                json=delivery.payload,
                headers={
                    "X-HookScope-Delivery-ID": str(delivery.id),
                },
            )

            attempt.status_code = response.status_code
            attempt.response_body = response.text[:MAX_RESPONSE_LENGHT] 
            attempt.succeeded = 200 <= response.status_code < 300

    except httpx.RequestError as error:
        attempt.succeeded = False
        attempt.error_message = str(error)

    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    return attempt