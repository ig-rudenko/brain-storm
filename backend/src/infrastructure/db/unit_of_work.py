from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.common.unit_of_work import UnitOfWork
from src.infrastructure.db.repositories.agent_repo import SqlAlchemyAgentRepository
from src.infrastructure.db.repositories.user_repo import SqlAlchemyUserRepository
from src.infrastructure.db.repositories.dialog_repo import SqlAlchemyDialogRepository
from src.infrastructure.db.repositories.message_repo import SqlAlchemyMessageRepository


class SqlAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.agents = SqlAlchemyAgentRepository(session)
        self.users = SqlAlchemyUserRepository(session)
        self.dialogs = SqlAlchemyDialogRepository(session)
        self.messages = SqlAlchemyMessageRepository(session)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        else:
            await self.commit()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
