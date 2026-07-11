import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

class EndpointCreate(BaseModel):
    name: str
    destination_url: str | None = None

class EndpointResponse(BaseModel):
    id: uuid.UUID
    name: str
    token: str
    destination_url: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)