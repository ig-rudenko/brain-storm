import asyncio
from uuid import UUID

from src.domain.dialogs.services import send_message, start_dialog

from ...domain.common.exceptions import ValidationError
from ...domain.common.unit_of_work import UnitOfWork
from ...domain.dialogs.entities import Dialog
from ...domain.messages.entities import AuthorType, Message
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
            if not cmd.agent_ids:
                raise ValidationError("Must have at least one agent to start dialog")

            agents = []
            for aid in cmd.agent_ids:
                if agent := await self.uow.agents.get_by_id(aid):
                    agents.append(agent)
                else:
                    raise ValidationError(
                        f"Agent with id {aid} not found. Only active agents can be in dialog"
                    )

            dialog = start_dialog(user, agents, cmd.name)

            await self.uow.dialogs.add(dialog)
        return DialogDTO(
            id=dialog.id, name=dialog.name, agents=[agent.id for agent in dialog.agents], user_id=user_id
        )

    async def handle_send_message(self, cmd: SendMessageCommand) -> list[MessageDTO]:
        async with self.uow:
            dialog = await self.uow.dialogs.get_by_id(cmd.dialog_id)
            if dialog is None:
                raise ValidationError(f"Dialog with id {cmd.dialog_id} not found")

            if cmd.author_type == AuthorType.AGENT:
                sender = await self.uow.agents.get_by_id(cmd.author_id)
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

            if cmd.author_type == AuthorType.USER:
                # Если отправитель - пользователь, то нужно сгенерировать ответы для всех агентов
                return await self._generate_llm_response(dialog)

        return [self._message_to_dto(msg)]

    async def _generate_llm_response(self, dialog: Dialog) -> list[MessageDTO]:
        messages = await self.uow.messages.get_by_dialog_id(dialog.id, limit=20, offset=0)

        tasks = []
        for agent in dialog.agents:
            # Только сообщения от пользователя и самого агента
            messages_for_agent = [
                message
                for message in messages
                if message.author_id == agent.id or message.author_type != AuthorType.AGENT
            ]
            tasks.append(asyncio.create_task(self.llm.generate(agent.prompt, messages_for_agent)))

        responses: list[str] = await asyncio.gather(*tasks, return_exceptions=True)

        response_messages: list[MessageDTO] = []
        for agent, response in zip(dialog.agents, responses):
            if isinstance(response, Exception):
                print(f"Error generating response for agent {agent.id}: {response}")
                continue
            if response:
                msg = send_message(dialog, agent, response)
                await self.uow.messages.add(msg)
                response_messages.append(self._message_to_dto(msg))

        return response_messages

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
