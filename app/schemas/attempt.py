import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

class DeliveryAttemptResponse(BaseModel):
    id: uuid.UUID
    delivery_id: uuid.UUID
    attempt_number: int
    succeeded: bool
    status_code: int | None
    response_body: str |None
    error_message: str | None
    attempted_at: datetime
    model_config = ConfigDict(
        from_attributes=True,
    )