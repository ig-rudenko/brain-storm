from dataclasses import dataclass, field
from typing import List, Self
from uuid import UUID, uuid4

from ..common.exceptions import ValidationError
from ..messages.entities import Message


@dataclass(slots=True)
class Dialog:
    id: UUID
    user_id: UUID
    pipeline_id: UUID
    name: str
    messages: List[Message] = field(default_factory=list)

    @classmethod
    def create(cls, *, name: str, user_id: UUID, pipeline_id: UUID) -> Self:
        if not name:
            raise ValidationError("Dialog name cannot be empty")
        return cls(id=uuid4(), user_id=user_id, name=name, pipeline_id=pipeline_id)
