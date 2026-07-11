import secrets

from fastapi import APIRouter, Depends, status

from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.database.models.endpoint import WebhookEndpoint
from app.schemas.endpoint import EndpointCreate, EndpointResponse

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