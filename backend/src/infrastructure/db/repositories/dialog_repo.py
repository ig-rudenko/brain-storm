from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.domain.dialogs.entities import Dialog
from src.domain.agents.entities import Agent
from src.domain.dialogs.repository import DialogRepository
from src.infrastructure.db.models import DialogModel, AgentModel


class SqlAlchemyDialogRepository(DialogRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, dialog_id: UUID) -> Dialog | None:
        stmt = select(DialogModel).where(DialogModel.id == dialog_id)
        result = await self.session.execute(stmt)
        row = result.scalar_one_or_none()
        return self._to_domain(row) if row else None

    async def get_user_dialogs(self, user_id: UUID) -> list[Dialog]:
        stmt = select(DialogModel).where(DialogModel.user_id == user_id)
        result = await self.session.execute(stmt)
        return [self._to_domain(r) for r in result.scalars().all()]

    async def add(self, dialog: Dialog) -> Dialog:
        # создаём ORM-модель
        model = DialogModel(
            id=dialog.id,
            name=dialog.name,
            user_id=dialog.user_id,
        )
        # связываем агентов через many-to-many
        if dialog.agents:
            agents = await self.session.execute(select(AgentModel).where(AgentModel.id.in_(dialog.agents)))
            model.agents = list(agents.scalars().all())

        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_domain(model)

    async def update(self, dialog: Dialog) -> Dialog | None:
        stmt = select(DialogModel).where(DialogModel.id == dialog.id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is not None:
            model.name = dialog.name

            # обновляем many-to-many связи с агентами
            if dialog.agents is not None:
                agents = await self.session.execute(
                    select(AgentModel).where(AgentModel.id.in_(dialog.agents))
                )
                model.agents = list(agents.scalars().all())

            await self.session.flush()
            await self.session.refresh(model)
            return self._to_domain(model)

    async def delete(self, dialog_id: UUID) -> None:
        stmt = select(DialogModel).where(DialogModel.id == dialog_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is not None:
            await self.session.delete(model)
            await self.session.flush()

    @staticmethod
    def _to_domain(model: DialogModel) -> Dialog:
        return Dialog(
            id=model.id,
            name=model.name,
            user_id=model.user_id,
            agents=[
                Agent.create(
                    name=agent.name,
                    description=agent.description,
                    prompt=agent.prompt,
                    temperature=agent.temperature,
                )
                for agent in model.agents
            ],
        )
