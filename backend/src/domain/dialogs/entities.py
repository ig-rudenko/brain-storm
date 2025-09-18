from uuid import UUID, uuid4
from dataclasses import dataclass, field
from typing import List, Self, Any

from ..agents.entities import Agent
from ..common.exceptions import ValidationError, UnauthorizedError
from ..messages.entities import Message
from ..users.entities import User


@dataclass(slots=True)
class Dialog:
    id: UUID
    user_id: UUID
    name: str
    agents: List[Agent] = field(default_factory=list)
    messages: List[Message] = field(default_factory=list)

    @classmethod
    def create(cls, user_id: UUID, name: str) -> Self:
        if not name:
            raise ValidationError("Dialog name cannot be empty")
        return cls(id=uuid4(), user_id=user_id, name=name)

    def add_agent(self, agent: Agent) -> None:
        for agent_ in self.agents:
            if agent_.id == agent.id:
                raise ValidationError(f"Agent with id {agent.id} already exists in dialog")
            else:
                self.agents.append(agent)

    def remove_agent(self, agent: Agent) -> None:
        for agent_ in self.agents:
            if agent_.id == agent.id:
                self.agents.remove(agent)
                break
        else:
            raise ValidationError(f"Agent with id {agent.id} not found in dialog")

    def post_user_message(self, user: User, text: str, metadata: dict[str, Any] | None = None) -> Message:
        # Правило: только владелец диалога (или участник) может писать? Здесь допускаем только владелец как упрощение
        if user.id != self.user_id:
            raise UnauthorizedError(
                "Только владелец диалога может писать в него (правило по умолчанию). Измените бизнес-правило при необходимости."
            )
        msg = Message.from_user(dialog_id=self.id, user_id=user.id, text=text, metadata=metadata)
        self.messages.append(msg)
        return msg

    def post_agent_message(self, agent: Agent, text: str, metadata: dict[str, Any] | None = None) -> Message:
        # Правило: агент должен быть добавлен и активен
        if not any(a.id == agent.id for a in self.agents):
            raise UnauthorizedError("Агент не является участником диалога")
        msg = Message.from_agent(dialog_id=self.id, agent_id=agent.id, text=text, metadata=metadata)
        self.messages.append(msg)
        return msg
