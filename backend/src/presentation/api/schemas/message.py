from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from src.domain.messages.entities import AuthorType


class MessageSchema(BaseModel):
    id: UUID
    text: str
    dialog_id: UUID
    author_id: UUID
    author_type: AuthorType
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        orm_mode = True


class MessagesResponseSchema(BaseModel):
    result: list[MessageSchema]
