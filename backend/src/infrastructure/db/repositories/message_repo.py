from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.domain.messages.entities import Message
from src.domain.messages.repository import MessageRepository
from src.infrastructure.db.models import MessageModel


class SqlAlchemyMessageRepository(MessageRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, message_id: UUID) -> Message | None:
        stmt = select(MessageModel).where(MessageModel.id == message_id)
        result = await self.session.execute(stmt)
        row = result.scalar_one_or_none()
        return self._to_domain(row) if row else None

    async def list_all(self) -> list[Message]:
        stmt = select(MessageModel)
        result = await self.session.execute(stmt)
        return [self._to_domain(r) for r in result.scalars().all()]

    async def add(self, message: Message) -> None:
        model = MessageModel(
            id=message.id,
            text=message.text,
            conversation_id=message.conversation_id,
            agent_id=message.agent_id,
        )
        self.session.add(model)
        await self.session.flush()

    async def update(self, message: Message) -> None:
        stmt = select(MessageModel).where(MessageModel.id == message.id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is not None:
            model.text = message.text
            await self.session.flush()

    async def delete(self, message_id: UUID) -> None:
        stmt = select(MessageModel).where(MessageModel.id == message_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is not None:
            await self.session.delete(model)
            await self.session.flush()

    @staticmethod
    def _to_domain(model: MessageModel) -> Message:
        return Message(
            id=model.id,
            text=model.text,
            conversation_id=model.conversation_id,
            agent_id=model.agent_id,
            user_id=model.user_id,
        )
