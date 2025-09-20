import re
from typing import Protocol

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.common.exceptions import DomainError, RepositoryError, UniqueError


class HasAsyncSession(Protocol):
    session: AsyncSession


class SqlAlchemyRepositoryMixin(HasAsyncSession):

    async def _flush_changes(self) -> None:
        try:
            await self.session.flush()
        except IntegrityError as exc:
            print(exc)
            raise self._parse_error(exc) from exc

    @staticmethod
    def _parse_error(exc: Exception) -> DomainError:
        if unique_field := re.search(r"UNIQUE constraint failed: (\S+)", str(exc)):
            part, _, field = unique_field.group(0).partition(".")
            field = field or part
            return UniqueError(f"UNIQUE constraint failed: {field}", field=field)
        return RepositoryError("Internal server error")
