from uuid import UUID, uuid4
from dataclasses import dataclass, field
from typing import List, Self


@dataclass(frozen=True, slots=True)
class Conversation:
    id: UUID
    user_id: UUID
    name: str
    agents: List[UUID] = field(default_factory=list)

    @classmethod
    def create(cls, user_id: UUID, name: str) -> Self:
        if not name:
            raise ValueError("Conversation name cannot be empty")
        return cls(id=uuid4(), user_id=user_id, name=name)

    def add_agent(self, agent_id: UUID) -> None:
        if agent_id not in self.agents:
            self.agents.append(agent_id)
