from uuid import UUID

from advanced_alchemy.filters import LimitOffset
from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.messages.entities import Message
from src.domain.messages.repository import MessageRepository
from src.infrastructure.db.exception_handler import wrap_sqlalchemy_exception
from src.infrastructure.db.models import MessageModel


class SQLMessageRepository(SQLAlchemyAsyncRepository[MessageModel]):
    model_type = MessageModel

    @property
    def dialect(self):
        return self._dialect


class SqlAlchemyMessageRepository(MessageRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
        self._repo = SQLMessageRepository(
            session=session, auto_commit=False, auto_refresh=True, wrap_exceptions=False
        )

    async def get_by_id(self, message_id: UUID) -> Message:
        with wrap_sqlalchemy_exception(self._repo.dialect):
            model = await self._repo.get(message_id)
        return self._to_domain(model)

    async def get_by_dialog_id(self, dialog_id: UUID, page: int, page_size: int) -> tuple[list[Message], int]:
        offset = (page - 1) * page_size
        with wrap_sqlalchemy_exception(self._repo.dialect):
            results, total = await self._repo.list_and_count(
                MessageModel.dialog_id == dialog_id, LimitOffset(offset=offset, limit=page_size)
            )
        return [self._to_domain(r) for r in results], total

    async def add(self, message: Message) -> Message:
        model = self._to_model(message)
        with wrap_sqlalchemy_exception(self._repo.dialect):
            model = await self._repo.add(model)
        return self._to_domain(model)

    async def add_many(self, messages: list[Message]) -> list[Message]:
        with wrap_sqlalchemy_exception(self._repo.dialect):
            await self._repo.add_many([self._to_model(m) for m in messages])
        return messages

    async def update(self, message: Message) -> Message:
        model = self._to_model(message)
        with wrap_sqlalchemy_exception(self._repo.dialect):
            model = await self._repo.update(
                model, attribute_names=["text", "dialog_id", "author_id", "author_type", "meta_data"]
            )
        return self._to_domain(model)

    async def delete(self, message_id: UUID) -> None:
        with wrap_sqlalchemy_exception(self._repo.dialect):
            await self._repo.delete(message_id)

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

    @staticmethod
    def _to_model(domain: Message) -> MessageModel:
        return MessageModel(
            id=domain.id,
            text=domain.text,
            dialog_id=domain.dialog_id,
            author_id=domain.author_id,
            author_type=domain.author_type,
            meta_data=domain.metadata,
        )
