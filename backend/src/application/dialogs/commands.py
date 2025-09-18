from pydantic import BaseModel
from uuid import UUID

from src.domain.messages.entities import AuthorType


class StartDialogCommand(BaseModel):
    name: str
    agent_ids: list[UUID]


class SendMessageCommand(BaseModel):
    dialog_id: UUID
    author_id: UUID
    author_type: AuthorType
    text: str
