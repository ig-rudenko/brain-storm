from dataclasses import dataclass
from typing import Self, Optional
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class Message:
    id: UUID
    text: str
    conversation_id: UUID
    user_id: UUID
    agent_id: Optional[UUID]

    @classmethod
    def create(cls, text: str, conversation_id: UUID, user_id: UUID, agent_id: UUID | None = None) -> Self:
        if not text:
            raise ValueError("Text cannot be empty")

        return cls(id=uuid4(), text=text, conversation_id=conversation_id, agent_id=agent_id, user_id=user_id)
