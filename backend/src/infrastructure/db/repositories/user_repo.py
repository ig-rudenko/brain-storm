from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.domain.users.entities import User
from src.domain.users.repository import UserRepository
from src.infrastructure.db.models import UserModel


class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: UUID) -> User | None:
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self.session.execute(stmt)
        row = result.scalar_one_or_none()
        return self._to_domain(row) if row else None

    async def list_all(self) -> list[User]:
        stmt = select(UserModel)
        result = await self.session.execute(stmt)
        return [self._to_domain(r) for r in result.scalars().all()]

    async def add(self, user: User) -> None:
        model = UserModel(
            id=user.id,
            name=user.name,
            description=user.description,
            prompt=user.prompt,
            temperature=user.temperature,
        )
        self.session.add(model)
        await self.session.flush()

    async def update(self, user: User) -> None:
        stmt = select(UserModel).where(UserModel.id == user.id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is not None:
            model.email = user.email
            model.first_name = user.first_name
            model.last_name = user.last_name
            model.is_superuser = user.is_superuser
            await self.session.flush()

    async def delete(self, user_id: UUID) -> None:
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is not None:
            await self.session.delete(model)
            await self.session.flush()

    @staticmethod
    def _to_domain(model: UserModel) -> User:
        return User(
            id=model.id,
            username=model.username,
            email=model.email,
            password=model.password,
            first_name=model.first_name,
            last_name=model.last_name,
            is_superuser=model.is_superuser,
            is_active=model.is_active,
        )
