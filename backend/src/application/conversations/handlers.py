from uuid import UUID

from src.domain.conversations.services import start_conversation, send_message
from .commands import StartConversationCommand, SendMessageCommand
from ...domain.common.unit_of_work import UnitOfWork


class ConversationHandler:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def handle_start(self, cmd: StartConversationCommand) -> UUID:
        with self.uow:
            user = await self.uow.users.get_by_id(cmd.user_id)
            if user is None:
                raise ValueError(f"User with id {cmd.user_id} not found")
            if not user.is_active:
                raise ValueError(
                    f"User with id {cmd.user_id} is not active. Only active users can start conversations"
                )
            if not cmd.agent_ids:
                raise ValueError(
                    f"User with id {cmd.user_id} must have at least one agent to start conversation"
                )

            agents = [await self.uow.agents.get_by_id(aid) for aid in cmd.agent_ids]

            conv = start_conversation(user, [a for a in agents if a], cmd.name)

            await self.uow.conversations.add(conv)
        return conv.id

    async def handle_send(self, cmd: SendMessageCommand) -> UUID:
        with self.uow:
            conv = await self.uow.conversations.get_by_id(cmd.conversation_id)
            if conv is None:
                raise ValueError(f"Conversation with id {cmd.conversation_id} not found")

            # sender может быть и User, и Agent
            sender = await self.uow.users.get_by_id(cmd.sender_id)
            if not sender:
                sender = await self.uow.agents.get_by_id(cmd.sender_id)

            if sender is None:
                raise ValueError(f"Sender with id {cmd.sender_id} not found")

            msg = send_message(conv, sender, cmd.text)
            await self.uow.messages.add(msg)
        return msg.id
