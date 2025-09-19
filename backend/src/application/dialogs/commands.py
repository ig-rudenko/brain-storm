from uuid import UUID

from pydantic import BaseModel

from src.domain.messages.entities import AuthorType


class StartDialogCommand(BaseModel):
    name: str
    pipeline_id: UUID


class SendMessageCommand(BaseModel):
    dialog_id: UUID
    author_id: UUID
    author_type: AuthorType
    text: str
