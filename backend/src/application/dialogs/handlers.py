from uuid import UUID

from src.domain.agents.entities import Agent
from src.domain.common.exceptions import ValidationError
from src.domain.common.unit_of_work import UnitOfWork
from src.domain.dialogs.services import send_message, start_dialog
from src.domain.messages.entities import AuthorType, Message
from src.domain.users.entities import User

from ..messages.dto import MessageDTO
from ..services import AgentLLMClient
from .commands import SendMessageCommand, StartDialogCommand
from .dto import DialogDTO


class DialogHandler:
    def __init__(self, uow: UnitOfWork, llm: AgentLLMClient):
        self.uow = uow
        self.llm = llm

    async def handle_start_dialog(self, user_id: UUID, cmd: StartDialogCommand) -> DialogDTO:
        async with self.uow:
            user = await self.uow.users.get_by_id(user_id)
            if user is None:
                raise ValidationError(f"User with id {user_id} not found")
            if not user.is_active:
                raise ValidationError(
                    f"User with id {user_id} is not active. Only active users can start dialogs"
                )

            dialog = start_dialog(user=user, pipeline_id=cmd.pipeline_id, name=cmd.name)

            await self.uow.dialogs.add(dialog)
        return DialogDTO(id=dialog.id, name=dialog.name, user_id=user_id, pipeline_id=cmd.pipeline_id)

    async def handle_send_message(self, cmd: SendMessageCommand) -> list[MessageDTO]:
        async with self.uow:
            dialog = await self.uow.dialogs.get_by_id(cmd.dialog_id)
            if dialog is None:
                raise ValidationError(f"Dialog with id {cmd.dialog_id} not found")

            if cmd.author_type == AuthorType.AGENT:
                sender: User | Agent | None = await self.uow.agents.get_by_id(cmd.author_id)
            if cmd.author_type == AuthorType.USER:
                sender = await self.uow.users.get_by_id(cmd.author_id)
            else:
                raise ValidationError(f"Unknown author type {cmd.author_type}")
            if sender is None:
                if cmd.author_type == AuthorType.AGENT:
                    raise ValidationError(f"Agent with id {cmd.author_id} not found")
                else:
                    raise ValidationError(f"User with id {cmd.author_id} not found")

            msg = send_message(dialog, sender, cmd.text)
            await self.uow.messages.add(msg)

        return [self._message_to_dto(msg)]

    @staticmethod
    def _message_to_dto(msg: Message) -> MessageDTO:
        return MessageDTO(
            id=msg.id,
            text=msg.text,
            author_type=msg.author_type,
            author_id=msg.author_id,
            dialog_id=msg.dialog_id,
            created_at=msg.created_at,
            updated_at=msg.updated_at,
        )
