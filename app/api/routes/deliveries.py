import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.database.models.attempt import DeliveryAttempt
from app.database.models.delivery import Delivery
from app.database.models.endpoint import WebhookEndpoint

from app.schemas.attempt import DeliveryAttemptResponse
from app.schemas.delivery import DeliveryResponse

from app.services.forwarding import forward_delivery

router = APIRouter(
    prefix="/deliveries",
    tags=["Deliveries"],
)

@router.get("", response_model=list[DeliveryResponse])
def list_deliveries(
    db: Session = Depends(get_db),
):
    query = select(Delivery).order_by(
        Delivery.received_at.desc(),
    )

    deliveries = db.scalars(query).all()

    return deliveries

@router.get("/{delivery_id}", response_model=DeliveryResponse)
def get_delivery(
    delivery_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    
    delivery = db.get(
        Delivery,
        delivery_id,
    )

    if delivery is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery not found"
        )
    
    return delivery

@router.get(
    "/{delivery_id}/attempts",
    response_model=list[DeliveryAttemptResponse],
)
def list_delivery_attempts(
    delivery_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    delivery = db.get(
        Delivery,
        delivery_id,
    )

    if delivery is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery not found",
        )
    
    query = (
        select(DeliveryAttempt)
        .where(DeliveryAttempt.delivery_id == delivery_id)
        .order_by(DeliveryAttempt.attempt_number.asc())
    )

    attempts = db.scalars(query).all()

    return attempts

@router.post(
    "/{delivery_id}/retry",
    response_model=DeliveryAttemptResponse,
    status_code=status.HTTP_201_CREATED,
)
async def retry_delivery(
    delivery_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    delivery = db.get(
        Delivery,
        delivery_id,
    )

    if delivery is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = "Delivery not found",
        )
    
    endpoint = db.get(
        WebhookEndpoint,
        delivery.endpoint_id,
    )

    if endpoint is None or endpoint.destination_url is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This delivery has no destination URL",
        )
    
    attempt = await forward_delivery(
        delivery=delivery,
        destination_url=endpoint.destination_url,
        db=db,
    )

    return attempt

