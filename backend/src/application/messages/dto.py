from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from src.domain.messages.entities import AuthorType


@dataclass(frozen=True, slots=True)
class MessageDTO:
    id: UUID
    text: str
    dialog_id: UUID
    author_id: UUID
    author_type: AuthorType
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
