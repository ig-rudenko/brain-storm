from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.messages.entities import Message
from src.domain.messages.repository import MessageRepository
from src.infrastructure.db.models import MessageModel

from .mixins import SqlAlchemyRepositoryMixin


class SqlAlchemyMessageRepository(MessageRepository, SqlAlchemyRepositoryMixin):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, message_id: UUID) -> Message | None:
        stmt = select(MessageModel).where(MessageModel.id == message_id)
        result = await self.session.execute(stmt)
        row = result.scalar_one_or_none()
        return self._to_domain(row) if row else None

    async def get_by_dialog_id(self, dialog_id: UUID, limit: int = 10, offset: int = 0) -> list[Message]:
        stmt = (
            select(MessageModel)
            .limit(limit)
            .offset(offset)
            .where(MessageModel.dialog_id == dialog_id)
            .order_by(MessageModel.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return [self._to_domain(r) for r in result.scalars().all()]

    async def add(self, message: Message) -> Message:
        model = MessageModel(
            id=message.id,
            text=message.text,
            dialog_id=message.dialog_id,
            author_id=message.author_id,
            author_type=message.author_type,
            meta_data=message.metadata,
        )
        self.session.add(model)
        await self._flush_changes()
        await self.session.refresh(model)
        return self._to_domain(model)

    async def update(self, message: Message) -> Message | None:
        stmt = select(MessageModel).where(MessageModel.id == message.id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is not None:
            model.text = message.text
            await self._flush_changes()
            await self.session.refresh(model)
            return self._to_domain(model)

    async def delete(self, message_id: UUID) -> None:
        stmt = select(MessageModel).where(MessageModel.id == message_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is not None:
            await self.session.delete(model)
            await self._flush_changes()

    @staticmethod
    def _to_domain(model: MessageModel) -> Message:
        return Message(
            id=model.id,
            text=model.text,
            dialog_id=model.dialog_id,
            author_id=model.author_id,
            author_type=model.author_type,
            metadata=model.meta_data,
        )
