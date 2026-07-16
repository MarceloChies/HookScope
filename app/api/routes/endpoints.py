import secrets
import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.database.models.attempt import DeliveryAttempt
from app.database.models.delivery import Delivery
from app.database.models.endpoint import WebhookEndpoint
from app.schemas.endpoint import ContractBaselineUpdate, EndpointCreate, EndpointResponse, EndpointStatsResponse, EndpointUpdate

router = APIRouter(
    prefix="/endpoints", 
    tags=["Endpoints"])

@router.post(
    "",
    response_model=EndpointResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_endpoint(
    data: EndpointCreate,
    db: Session = Depends(get_db),
):
    endpoint = WebhookEndpoint(
        name=data.name,
        destination_url=data.destination_url,
        token=secrets.token_urlsafe(24),
    )

    db.add(endpoint)
    db.commit()
    db.refresh(endpoint)

    return endpoint

@router.get(
    "",
    response_model=list[EndpointResponse],
)
def list_endpoints(
    db: Session = Depends(get_db),
):
    query = select(WebhookEndpoint).order_by(
        WebhookEndpoint.created_at.desc(),
    )

    endpoints = db.scalars(query).all()

    return endpoints

@router.get(
    "/{endpoint_id}",
    response_model=EndpointResponse,
)
def get_endpoint(
    endpoint_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    endpoint = db.get(
        WebhookEndpoint,
        endpoint_id,
    )

    if endpoint is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Endpoint not Found",
        )
    
    return endpoint

@router.patch(
    "/{endpoint_id}",
    response_model=EndpointResponse,
)
def update_endpoint(
    endpoint_id: uuid.UUID,
    data: EndpointUpdate,
    db: Session = Depends(get_db),
):
    endpoint = db.get(
        WebhookEndpoint,
        endpoint_id,
    )

    if endpoint is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Endpoint not found",
        )
    
    updates = data.model_dump(exclude_unset=True)
    for field,value in updates.items():
        setattr(endpoint, field, value)

    db.commit()
    db.refresh(endpoint)

    return endpoint

@router.delete(
    "/{endpoint_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_endpoint(
    endpoint_id:  uuid.UUID,
    db: Session = Depends(get_db),
):
    endpoint = db.get(
        WebhookEndpoint,
        endpoint_id
        )

    if endpoint is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = "Endpoint not found",
        )
    
    db.delete(endpoint)
    db.commit()

    return None

@router.get(
    "/{endpoint_id}/stats",
    response_model=EndpointStatsResponse,
)
def get_endpoint_stats(
    endpoint_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    endpoint = db.get(WebhookEndpoint, endpoint_id)

    if endpoint is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Endpoint not found",
        )
    
    total_deliveries = db.scalar(
        select(func.count(Delivery.id)).where(
            Delivery.endpoint_id == endpoint_id,
        )
    ) or 0

    total_attempts = db.scalar(
        select(func.count(DeliveryAttempt.id))
        .join(Delivery)
        .where(
            Delivery.endpoint_id == endpoint_id,
        )
    ) or 0

    successful_attempts = db.scalar(
        select(func.count(DeliveryAttempt.id))
        .join(Delivery)
        .where(
            Delivery.endpoint_id == endpoint_id,
            DeliveryAttempt.succeeded.is_(True),
        )
    ) or 0

    failed_attempts = db.scalar(
        select(func.count(DeliveryAttempt.id))
        .join(Delivery)
        .where(
            Delivery.endpoint_id == endpoint_id,
            DeliveryAttempt.succeeded.is_(False),
        )
    ) or 0

    last_received_at = db.scalar(
        select(func.max(Delivery.received_at)).where(
            Delivery.endpoint_id == endpoint_id,
        )
    )

    return{
        "endpoint_id": endpoint_id,
        "total_deliveries": total_deliveries,
        "total_attempts": total_attempts,
        "successful_attempts": successful_attempts,
        "failed_attempts": failed_attempts,
        "last_received_at": last_received_at,
    }

@router.put(
    "/{endpoint_id}/contract",
    response_model=EndpointResponse,
)
def set_endpoint_contract(
    endpoint_id: uuid.UUID,
    data: ContractBaselineUpdate,
    db: Session = Depends(get_db),
):
    endpoint = db.get(
        WebhookEndpoint,
        endpoint_id,
    )

    if endpoint is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Endpoint not found",
        )
    
    endpoint.contract_baseline = data.contract_baseline

    db.commit()
    db.refresh(endpoint)

    return endpoint