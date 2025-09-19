from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.users.entities import User
from src.domain.users.repository import UserRepository
from src.infrastructure.db.models import UserModel

from .mixins import SqlAlchemyRepositoryMixin


class SqlAlchemyUserRepository(UserRepository, SqlAlchemyRepositoryMixin):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: UUID) -> User | None:
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self.session.execute(stmt)
        row = result.scalar_one_or_none()
        return self._to_domain(row) if row else None

    async def get_by_username(self, username: str) -> User | None:
        stmt = select(UserModel).where(UserModel.username == username)
        result = await self.session.execute(stmt)
        row = result.scalar_one_or_none()
        return self._to_domain(row) if row else None

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(UserModel).where(UserModel.email == email)
        result = await self.session.execute(stmt)
        row = result.scalar_one_or_none()
        return self._to_domain(row) if row else None

    async def list_all(self) -> list[User]:
        stmt = select(UserModel)
        result = await self.session.execute(stmt)
        return [self._to_domain(r) for r in result.scalars().all()]

    async def add(self, user: User) -> User:
        model = UserModel(
            id=user.id,
            username=user.username,
            password=user.password_hash,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_superuser=user.is_superuser,
            is_active=user.is_active,
        )

        self.session.add(model)
        await self._flush_changes()
        await self.session.refresh(model)
        return self._to_domain(model)

    async def update(self, user: User) -> User | None:
        stmt = select(UserModel).where(UserModel.id == user.id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is not None:
            model.username = user.username
            model.password = user.password_hash
            model.email = user.email
            model.first_name = user.first_name
            model.last_name = user.last_name
            model.is_superuser = user.is_superuser
            await self._flush_changes()
            await self.session.refresh(model)
            return self._to_domain(model)

    async def delete(self, user_id: UUID) -> None:
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is not None:
            await self.session.delete(model)
            await self._flush_changes()

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
