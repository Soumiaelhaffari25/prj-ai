import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    # Historique des messages, stocké en JSON (liste de {role, content})
    messages: Mapped[str] = mapped_column(Text, default="[]")
    # Infos BANT collectées jusqu'ici, en JSON
    collected_data: Mapped[str] = mapped_column(Text, default="{}")
    # État : "en_cours" ou "terminée"
    status: Mapped[str] = mapped_column(String, default="en_cours")
    # Lead créé à la fin (rempli une fois la conversation terminée)
    lead_id: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )