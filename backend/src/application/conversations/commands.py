from pydantic import BaseModel
from uuid import UUID


class StartConversationCommand(BaseModel):
    user_id: UUID
    agent_ids: list[UUID]
    name: str


class SendMessageCommand(BaseModel):
    conversation_id: UUID
    sender_id: UUID
    text: str
