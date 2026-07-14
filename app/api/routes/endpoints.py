import secrets
import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.database.models.endpoint import WebhookEndpoint
from app.schemas.endpoint import EndpointCreate, EndpointResponse, EndpointUpdate

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