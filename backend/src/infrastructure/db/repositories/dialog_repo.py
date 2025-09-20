from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.dialogs.entities import Dialog
from src.domain.dialogs.repository import DialogRepository
from src.infrastructure.db.models import DialogModel

from .mixins import SqlAlchemyRepositoryMixin


class SqlAlchemyDialogRepository(DialogRepository, SqlAlchemyRepositoryMixin):
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
            pipeline_id=dialog.pipeline_id,
        )
        self.session.add(model)
        await self._flush_changes()
        await self.session.refresh(model)
        return self._to_domain(model)

    async def update(self, dialog: Dialog) -> Dialog | None:
        stmt = select(DialogModel).where(DialogModel.id == dialog.id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is not None:
            model.name = dialog.name
            await self._flush_changes()
            await self.session.refresh(model)
            return self._to_domain(model)
        return None

    async def delete(self, dialog_id: UUID) -> None:
        stmt = select(DialogModel).where(DialogModel.id == dialog_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is not None:
            await self.session.delete(model)
            await self._flush_changes()
        return None

    @staticmethod
    def _to_domain(model: DialogModel) -> Dialog:
        return Dialog(
            id=model.id,
            name=model.name,
            user_id=model.user_id,
            pipeline_id=model.pipeline_id,
        )
