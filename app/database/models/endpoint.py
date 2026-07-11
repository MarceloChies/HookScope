import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base

class WebhookEndpoint(Base):
    __tablename__ = "webhook_endpoints"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str]= mapped_column(String(100))
    token: Mapped[str] = mapped_column(
        String(64),
        unique = True,
        index = True,
    )
    destination_url: Mapped[str | None] = mapped_column(
        String(2048),
        nullable= True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    deliveries: Mapped[list["Delivery"]] = relationship(
        back_populates="endpoint",
        cascade="all, delete-orphan",
    )