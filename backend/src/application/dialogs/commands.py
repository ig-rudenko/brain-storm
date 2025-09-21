from dataclasses import dataclass
from uuid import UUID

from src.domain.messages.entities import AuthorType


@dataclass(slots=True, frozen=True, kw_only=True)
class StartDialogCommand:
    user_id: UUID
    name: str
    pipeline_id: UUID


@dataclass(slots=True, frozen=True, kw_only=True)
class SendMessageCommand:
    dialog_id: UUID
    author_id: UUID
    author_type: AuthorType
    text: str
