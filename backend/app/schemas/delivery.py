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
    contract_valid: bool | None = None
    contract_issues: list[dict[str,str]] | None = None
    received_at: datetime
    duplicate_of_id: uuid.UUID | None = None
    model_config = ConfigDict(
        from_attributes=True,
    )