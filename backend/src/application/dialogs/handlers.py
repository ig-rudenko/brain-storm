from src.domain.common.exceptions import ValidationError
from src.domain.common.unit_of_work import UnitOfWork
from src.domain.dialogs.services import start_dialog
from src.domain.messages.entities import Message

from ..messages.dto import MessageDTO
from ..services import AgentLLMClient
from .commands import StartDialogCommand
from .dto import DialogDTO


class DialogHandler:
    def __init__(self, uow: UnitOfWork, llm: AgentLLMClient):
        self.uow = uow
        self.llm = llm

    async def handle_start_dialog(self, cmd: StartDialogCommand) -> DialogDTO:
        async with self.uow:
            user = await self.uow.users.get_by_id(cmd.user_id)
            if user is None:
                raise ValidationError(f"User with id {cmd.user_id} not found")
            if not user.is_active:
                raise ValidationError(
                    f"User with id {cmd.user_id} is not active. Only active users can start dialogs"
                )

            dialog = start_dialog(user=user, pipeline_id=cmd.pipeline_id, name=cmd.name)

            await self.uow.dialogs.add(dialog)
        return DialogDTO(id=dialog.id, name=dialog.name, user_id=cmd.user_id, pipeline_id=cmd.pipeline_id)

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
