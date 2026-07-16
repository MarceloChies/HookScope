import uuid

from typing import Any
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
    contract_baseline: dict[str, Any] | None = None
    model_config = ConfigDict(from_attributes=True)

class EndpointUpdate(BaseModel):
    name : str | None = None
    destination_url: str | None = None

class EndpointStatsResponse(BaseModel):
    endpoint_id: uuid.UUID
    total_deliveries: int
    total_attempts: int
    successful_attempts: int
    failed_attempts: int
    last_received_at: datetime | None

class ContractBaselineUpdate(BaseModel):
    contract_baseline: dict[str, Any]