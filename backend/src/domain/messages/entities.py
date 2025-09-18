from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Self, Optional, Any
from uuid import UUID, uuid4

from src.domain.common.exceptions import ValidationError


class AuthorType(str, Enum):
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"


@dataclass(slots=True)
class Message:
    id: UUID
    dialog_id: UUID
    author_id: UUID
    author_type: AuthorType
    text: str
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_user(
        cls, dialog_id: UUID, user_id: UUID, text: str, metadata: dict[str, Any] | None = None
    ) -> Self:
        text = text.strip()
        if not text:
            raise ValueError("Text cannot be empty")
        return cls(
            id=uuid4(),
            text=text,
            dialog_id=dialog_id,
            author_id=user_id,
            author_type=AuthorType.USER,
            metadata=metadata or {},
        )

    @classmethod
    def from_agent(
        cls, dialog_id: UUID, agent_id: UUID, text: str, metadata: dict[str, Any] | None = None
    ) -> Self:
        if not text:
            raise ValidationError("Text cannot be empty")
        return cls(
            id=uuid4(), text=text, dialog_id=dialog_id, author_id=agent_id, author_type=AuthorType.AGENT
        )
