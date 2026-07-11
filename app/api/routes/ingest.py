from fastapi import APIRouter, Depends, HTTPException, Request, status 
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.database.models.delivery import Delivery
from app.database.models.endpoint import WebhookEndpoint

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
    
    delivery = Delivery(
        endpoint_id = endpoint.id,
        method=request.method,
        headers=dict(request.headers),
        payload=payload,
    )

    db.add(delivery)
    db.commit()
    db.refresh(delivery)

    return{
        "message": "Webhook recieved",
        "delivery_id": str(delivery.id),
    }