from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.domain.conversations.entities import Conversation
from src.domain.conversations.repository import ConversationRepository
from src.infrastructure.db.models import ConversationModel, AgentModel


class SqlAlchemyConversationRepository(ConversationRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, conversation_id: UUID) -> Conversation | None:
        stmt = select(ConversationModel).where(ConversationModel.id == conversation_id)
        result = await self.session.execute(stmt)
        row = result.scalar_one_or_none()
        return self._to_domain(row) if row else None

    async def list_all(self) -> list[Conversation]:
        stmt = select(ConversationModel)
        result = await self.session.execute(stmt)
        return [self._to_domain(r) for r in result.scalars().all()]

    async def add(self, conversation: Conversation) -> None:
        # создаём ORM-модель
        model = ConversationModel(
            id=conversation.id,
            name=conversation.name,
            user_id=conversation.user_id,
        )
        # связываем агентов через many-to-many
        if conversation.agents:
            agents = await self.session.execute(
                select(AgentModel).where(AgentModel.id.in_(conversation.agents))
            )
            model.agents = list(agents.scalars().all())

        self.session.add(model)
        await self.session.flush()

    async def update(self, conversation: Conversation) -> None:
        stmt = select(ConversationModel).where(ConversationModel.id == conversation.id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is not None:
            model.name = conversation.name

            # обновляем many-to-many связи с агентами
            if conversation.agents is not None:
                agents = await self.session.execute(
                    select(AgentModel).where(AgentModel.id.in_(conversation.agents))
                )
                model.agents = list(agents.scalars().all())

            await self.session.flush()

    async def delete(self, conversation_id: UUID) -> None:
        stmt = select(ConversationModel).where(ConversationModel.id == conversation_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is not None:
            await self.session.delete(model)
            await self.session.flush()

    @staticmethod
    def _to_domain(model: ConversationModel) -> Conversation:
        return Conversation(
            id=model.id,
            name=model.name,
            user_id=model.user_id,
            agents=[a.id for a in model.agents],  # возвращаем список UUID
        )
