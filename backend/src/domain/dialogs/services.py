from typing import Any
from uuid import UUID

from src.domain.agents.entities import Agent
from src.domain.dialogs.entities import Dialog
from src.domain.messages.entities import Message
from src.domain.users.entities import User


def start_dialog(*, user: User, pipeline_id: UUID, name: str) -> Dialog:
    """Создать новый разговор между пользователем и агентами."""
    if not user.is_active:
        raise ValueError("Inactive user cannot start dialog")

    dialog = Dialog.create(name=name, user_id=user.id, pipeline_id=pipeline_id)
    return dialog


def send_message(
    dialog: Dialog, sender: User | Agent, text: str, metadata: dict[str, Any] | None = None
) -> Message:
    """Отправить сообщение от пользователя или агента."""
    if isinstance(sender, User) and not sender.is_active:
        raise ValueError("Inactive user cannot send messages")

    if isinstance(sender, Agent):
        return Message.from_agent(dialog_id=dialog.id, text=text, agent_id=sender.id, metadata=metadata)
    else:
        return Message.from_user(dialog_id=dialog.id, text=text, user_id=sender.id, metadata=metadata)
