from uuid import UUID

import advanced_alchemy
from advanced_alchemy.filters import LimitOffset
from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.common.exceptions import ObjectNotFoundError
from src.domain.users.entities import User
from src.domain.users.repository import UserRepository
from src.infrastructure.db.models import UserModel

from .mixins import SqlAlchemyRepositoryMixin


class SQLUserRepository(SQLAlchemyAsyncRepository[UserModel]):
    model_type = UserModel


class SqlAlchemyUserRepository(UserRepository, SqlAlchemyRepositoryMixin):
    def __init__(self, session: AsyncSession):
        self.session = session
        self._repo = SQLUserRepository(session=session, auto_commit=False, auto_refresh=True)

    async def get_by_id(self, user_id: UUID) -> User:
        try:
            model = await self._repo.get(user_id)
        except advanced_alchemy.exceptions.NotFoundError as exc:
            raise ObjectNotFoundError(f"User with id {user_id} not found") from exc
        return self._to_domain(model)

    async def get_by_username(self, username: str) -> User:
        try:
            model = await self._repo.get_one(UserModel.username == username)
        except advanced_alchemy.exceptions.NotFoundError as exc:
            raise ObjectNotFoundError(f"User with username {username} not found") from exc
        return self._to_domain(model)

    async def get_by_email(self, email: str) -> User:
        try:
            model = await self._repo.get_one(UserModel.email == email)
        except advanced_alchemy.exceptions.NotFoundError as exc:
            raise ObjectNotFoundError(f"User with email {email} not found") from exc
        return self._to_domain(model)

    async def get_paginated(self, page: int, page_size: int) -> tuple[list[User], int]:
        offset = (page - 1) * page_size
        results, total = await self._repo.list_and_count(LimitOffset(offset=offset, limit=page_size))
        return [self._to_domain(r) for r in results], total

    async def add(self, user: User) -> User:
        model = self._to_model(user)
        model = await self._repo.add(model)
        return self._to_domain(model)

    async def update(self, user: User) -> User:
        model = self._to_model(user)
        try:
            model = await self._repo.update(
                model,
                attribute_names=[
                    "username",
                    "email",
                    "password_hash",
                    "first_name",
                    "last_name",
                    "is_superuser",
                    "is_active",
                ],
            )
        except advanced_alchemy.exceptions.NotFoundError as exc:
            raise ObjectNotFoundError(f"User with id {user.id} not found") from exc
        return self._to_domain(model)

    async def delete(self, user_id: UUID) -> None:
        try:
            await self._repo.delete(user_id)
        except advanced_alchemy.exceptions.NotFoundError as exc:
            raise ObjectNotFoundError(f"User with id {user_id} not found") from exc

    @staticmethod
    def _to_domain(model: UserModel) -> User:
        return User(
            id=model.id,
            username=model.username,
            email=model.email,
            password_hash=model.password,
            first_name=model.first_name,
            last_name=model.last_name,
            is_superuser=model.is_superuser,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _to_model(user: User) -> UserModel:
        return UserModel(
            id=user.id,
            username=user.username,
            password=user.password_hash,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_superuser=user.is_superuser,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
