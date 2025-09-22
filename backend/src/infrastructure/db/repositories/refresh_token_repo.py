from datetime import UTC, datetime
from uuid import UUID

import advanced_alchemy
from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy import update

from src.domain.auth.entities import JWToken
from src.domain.auth.repository import RefreshTokenRepository
from src.domain.common.exceptions import ObjectNotFoundError
from src.infrastructure.db.models import RefreshTokenModel


class SQLRefreshTokenRepository(SQLAlchemyAsyncRepository[RefreshTokenModel]):
    model_type = RefreshTokenModel


class SqlAlchemyRefreshTokenRepository(RefreshTokenRepository):
    def __init__(self, session):
        self.session = session
        self._repo = SQLRefreshTokenRepository(session=session, auto_commit=False, auto_refresh=True)

    async def get_by_hash(self, token_hash: str) -> JWToken:
        try:
            model = await self._repo.get_one(RefreshTokenModel.token_hash == token_hash)
        except advanced_alchemy.exceptions.NotFoundError as exc:
            raise ObjectNotFoundError("Refresh token not found or already revoked") from exc
        return self._to_domain(model)

    async def add(self, token: JWToken) -> JWToken:
        model = self._to_model(token)
        await self._repo.add(model)
        # self.session.add(model)
        # await self.session.flush()
        return token

    async def revoke(self, token_hash: str) -> None:
        try:
            token = await self._repo.get_one(RefreshTokenModel.token_hash == token_hash)
        except advanced_alchemy.exceptions.NotFoundError as exc:
            raise ObjectNotFoundError("Refresh token not found or already revoked") from exc
        if token.revoked:
            raise ObjectNotFoundError("Refresh token not found or already revoked")
        else:
            token.revoked = True
            await self._repo.update(token, attribute_names=["revoked"])

    async def revoke_all_for_user(self, user_id: UUID) -> None:
        stmt = update(RefreshTokenModel).where(RefreshTokenModel.user_id == user_id).values(revoked=True)
        await self.session.execute(stmt)

    @staticmethod
    def _to_domain(model: RefreshTokenModel) -> JWToken:
        return JWToken(
            id=model.id,
            token_hash=model.token_hash,
            user_id=model.user_id,
            issued_at=datetime.fromtimestamp(model.issued_at, UTC),
            expire_at=model.expire_at,
            revoked=model.revoked,
            token="",
        )

    @staticmethod
    def _to_model(domain: JWToken) -> RefreshTokenModel:
        return RefreshTokenModel(
            id=domain.id,
            token_hash=domain.token_hash,
            user_id=domain.user_id,
            issued_at=int(domain.issued_at.timestamp()),
            expire_at=domain.expire_at,
            revoked=domain.revoked,
        )
