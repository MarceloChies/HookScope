import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

class DeliveryResponse(BaseModel):
    id: uuid.UUID
    endpoint_id: uuid.UUID
    method: str
    headers: dict[str, Any]
    payload: dict[str, Any]
    received_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )