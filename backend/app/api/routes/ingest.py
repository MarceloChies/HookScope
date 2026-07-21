from fastapi import APIRouter, Depends, HTTPException, Request, status 
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.datastructures import Headers

from app.database.dependencies import get_db
from app.database.models.delivery import Delivery
from app.database.models.endpoint import WebhookEndpoint

from app.services.contract_watch import compare_payload_contract
from app.services.forwarding import forward_delivery
from app.services.idempotency import create_payload_fingerprint

router = APIRouter(
    prefix="/hooks",
    tags=["Webhook Ingestion"],
)

@router.post("/{token}", status_code=status.HTTP_202_ACCEPTED)
async def recieve_webhook(
    token: str,
    payload: dict,
    request: Request,
    db: Session = Depends(get_db),
):
    endpoint = db.scalar(
        select(WebhookEndpoint).where(WebhookEndpoint.token == token)
    )

    if endpoint is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook endpoint not found",
        )

    contract_valid = None
    contract_issues = None

    if endpoint.contract_baseline is not None:
        contract_issues = compare_payload_contract(
            baseline=endpoint.contract_baseline,
            payload=payload,
        )
    contract_valid = not contract_issues

    payload_fingerprint = None
    duplicate_of_id = None

    if endpoint.duplicate_detection_enabled:
        payload_fingerprint = create_payload_fingerprint(payload)

        original_delivery=db.scalar(
            select(Delivery).where(
                Delivery.endpoint_id == endpoint.id,
                Delivery.payload_fingerprint == payload_fingerprint,
            )
            .order_by(Delivery.received_at.asc())
            .limit(1)
        )

        if original_delivery is not None:
            duplicate_of_id = original_delivery.id

    delivery = Delivery(
        endpoint_id = endpoint.id,
        method=request.method,
        headers=sanitize_headers(request.headers),
        payload=payload,
        contract_valid=contract_valid,
        contract_issues=contract_issues,
        payload_fingerprint=payload_fingerprint,
        duplicate_of_id=duplicate_of_id,
    )

    db.add(delivery)
    db.commit()
    db.refresh(delivery)

    attempt= None

    if endpoint.destination_url:
        attempt = await forward_delivery(
            delivery=delivery,
            destination_url= endpoint.destination_url,
            db=db,
        )

    return{
        "message": "Webhook received",
        "delivery_id": str(delivery.id),
        "forwarded": attempt.succeeded if attempt else None,
        "destination_status": attempt.status_code if attempt else None,
        "duplicate": duplicate_of_id is not None,
        "duplicate_of_id": str(duplicate_of_id) if duplicate_of_id else None,
    }


SENSITIVE_HEADERS={
    "authorization",
    "cookie",
    "proxy-authorization",
    "set-cookie",
    "x-api-key",
}

def sanitize_headers(headers:Headers) -> dict[str, str]:
    return{
        name: "[REDACTED]" if name.lower() in SENSITIVE_HEADERS else value
        for name,value in headers.items()
    }