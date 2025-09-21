from uuid import UUID

import advanced_alchemy
from advanced_alchemy.filters import LimitOffset
from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.common.exceptions import ObjectNotFoundError
from src.domain.dialogs.entities import Dialog
from src.domain.dialogs.repository import DialogRepository
from src.infrastructure.db.models import DialogModel

from .mixins import SqlAlchemyRepositoryMixin


class SQLDialogRepository(SQLAlchemyAsyncRepository[DialogModel]):
    model_type = DialogModel


class SqlAlchemyDialogRepository(DialogRepository, SqlAlchemyRepositoryMixin):
    def __init__(self, session: AsyncSession):
        self.session = session
        self._repo = SQLDialogRepository(session=session, auto_commit=False, auto_refresh=True)

    async def get_by_id(self, dialog_id: UUID) -> Dialog:
        try:
            dialog = await self._repo.get(dialog_id)
        except advanced_alchemy.exceptions.NotFoundError as exc:
            raise ObjectNotFoundError(f"Dialog with id {dialog_id} not found") from exc
        return self._to_domain(dialog)

    async def get_user_dialogs(self, user_id: UUID, page: int, page_size: int) -> tuple[list[Dialog], int]:
        offset = (page - 1) * page_size
        results, total = await self._repo.list_and_count(
            DialogModel.user_id == user_id, LimitOffset(offset=offset, limit=page_size)
        )
        return [self._to_domain(r) for r in results], total

    async def add(self, dialog: Dialog) -> Dialog:
        model = self._to_model(dialog)
        model = await self._repo.add(model)
        return self._to_domain(model)

    async def update(self, dialog: Dialog) -> Dialog:
        model = self._to_model(dialog)
        try:
            model = await self._repo.update(model, attribute_names=["name", "pipeline_id", "user_id"])
        except advanced_alchemy.exceptions.NotFoundError as exc:
            raise ObjectNotFoundError(f"Dialog with id {dialog.id} not found") from exc
        return self._to_domain(model)

    async def delete(self, dialog_id: UUID) -> None:
        try:
            await self._repo.delete(dialog_id)
        except advanced_alchemy.exceptions.NotFoundError as exc:
            raise ObjectNotFoundError(f"Dialog with id {dialog_id} not found") from exc

    @staticmethod
    def _to_domain(model: DialogModel) -> Dialog:
        return Dialog(
            id=model.id,
            name=model.name,
            user_id=model.user_id,
            pipeline_id=model.pipeline_id,
        )

    @staticmethod
    def _to_model(dialog: Dialog) -> DialogModel:
        return DialogModel(
            id=dialog.id,
            name=dialog.name,
            user_id=dialog.user_id,
            pipeline_id=dialog.pipeline_id,
        )
