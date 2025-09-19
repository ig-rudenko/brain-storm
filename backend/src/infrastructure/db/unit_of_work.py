from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.common.unit_of_work import UnitOfWork
from src.infrastructure.db.repositories.agent_repo import SqlAlchemyAgentRepository
from src.infrastructure.db.repositories.dialog_repo import SqlAlchemyDialogRepository
from src.infrastructure.db.repositories.message_repo import SqlAlchemyMessageRepository
from src.infrastructure.db.repositories.pipeline_repo import (
    SqlAlchemyPipelineRepository,
)
from src.infrastructure.db.repositories.user_repo import SqlAlchemyUserRepository


class SqlAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session: AsyncSession):
        self._session = session
        self._agents: SqlAlchemyAgentRepository | None = None
        self._users: SqlAlchemyUserRepository | None = None
        self._dialogs: SqlAlchemyDialogRepository | None = None
        self._messages: SqlAlchemyMessageRepository | None = None
        self._pipelines: SqlAlchemyPipelineRepository | None = None

    @property
    def session(self) -> AsyncSession:
        return self._session

    @property
    def agents(self) -> SqlAlchemyAgentRepository:
        if self._agents is None:
            self._agents = SqlAlchemyAgentRepository(self._session)
        return self._agents

    @property
    def users(self) -> SqlAlchemyUserRepository:
        if self._users is None:
            self._users = SqlAlchemyUserRepository(self._session)
        return self._users

    @property
    def dialogs(self) -> SqlAlchemyDialogRepository:
        if self._dialogs is None:
            self._dialogs = SqlAlchemyDialogRepository(self._session)
        return self._dialogs

    @property
    def messages(self) -> SqlAlchemyMessageRepository:
        if self._messages is None:
            self._messages = SqlAlchemyMessageRepository(self._session)
        return self._messages

    @property
    def pipelines(self) -> SqlAlchemyPipelineRepository:
        if self._pipelines is None:
            self._pipelines = SqlAlchemyPipelineRepository(self._session)
        return self._pipelines

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        else:
            await self.commit()

    async def commit(self):
        await self._session.commit()

    async def rollback(self):
        await self._session.rollback()
