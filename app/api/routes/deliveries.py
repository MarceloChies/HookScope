import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.database.models.delivery import Delivery
from app.schemas.delivery import DeliveryResponse

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