from dataclasses import dataclass, field
from datetime import datetime
from typing import Self
from uuid import UUID

from src.domain.messages.entities import AuthorType, Message


@dataclass(frozen=True, slots=True, kw_only=True)
class MessageDTO:
    id: UUID
    text: str
    dialog_id: UUID
    author_id: UUID
    author_type: AuthorType
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    @classmethod
    def from_entity(cls, msg: Message) -> Self:
        return cls(
            id=msg.id,
            dialog_id=msg.dialog_id,
            text=msg.text,
            author_id=msg.author_id,
            author_type=msg.author_type,
            created_at=msg.created_at,
            updated_at=msg.updated_at,
        )
