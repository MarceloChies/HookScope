import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, JSON, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base

class Delivery(Base):
    __tablename__ = "deliveries"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    endpoint_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("webhook_endpoints.id", ondelete="CASCADE"),
        index = True,
    )
    method: Mapped[str] = mapped_column(String(10))
    headers: Mapped[dict[str, Any]] = mapped_column(JSON)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON)
    attempts: Mapped[list["DeliveryAttempt"]] = relationship(
        back_populates="delivery",
        cascade="all, delete-orphan",
    )
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    endpoint =  relationship("WebhookEndpoint", back_populates="deliveries")