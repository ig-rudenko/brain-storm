from src.application.users.commands import LoginUserCommand, RegisterUserCommand
from src.application.users.dto import JWTokenDTO, UserDTO
from src.domain.auth.services import AuthService
from src.domain.common.exceptions import (
    AuthorizationError,
    InvalidTokenError,
    ObjectNotFoundError,
)
from src.domain.common.unit_of_work import UnitOfWork
from src.domain.users.entities import User
from src.infrastructure.auth.hashers import PasswordHasherProtocol
from src.infrastructure.auth.token_service import JWTService


def get_dto(user: User) -> UserDTO:
    return UserDTO(
        id=user.id,
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


class RegisterUserHandler:
    def __init__(self, uow: UnitOfWork, hasher: PasswordHasherProtocol):
        self.uow = uow
        self.hasher = hasher

    async def handle(self, cmd: RegisterUserCommand) -> UserDTO:
        """
        Raises:
            UniqueError: если пользователь с таким email или username уже существует.
        """
        password_hash = self.hasher.hash(cmd.password)

        user = User.create(
            username=cmd.username,
            email=cmd.email,
            password_hash=password_hash,
            first_name=cmd.first_name,
            last_name=cmd.last_name,
        )

        async with self.uow:
            await self.uow.users.add(user)
            # commit произойдет автоматически

        return get_dto(user)


class JWTHandler:
    def __init__(self, uow: UnitOfWork, hasher: PasswordHasherProtocol, token_service: JWTService):
        self.uow = uow
        self.hasher = hasher
        self.token_service = token_service
        self.auth_service = AuthService(token_service, uow.refresh_token)

    async def handle_obtain_token(self, cmd: LoginUserCommand) -> JWTokenDTO:
        """
        Raises:
            ObjectNotFoundError: если пользователь не найден.
            AuthorizationError: если пользователь не найден или пароль неверный.
        """
        async with self.uow:
            user = await self.uow.users.get_by_username(cmd.username)
            if user is None or not self.hasher.verify(cmd.password, user.password_hash):
                raise AuthorizationError("Invalid email or password")
            if not user.is_active:
                raise AuthorizationError("User is inactive")

            tokens = await self.auth_service.login(user_id=user.id)
        return JWTokenDTO(access=tokens.access.token, refresh=tokens.refresh.token)

    async def handle_refresh_token(self, token: str) -> JWTokenDTO:
        """
        Raises:
            RefreshTokenRevokedError: если токен уже был использован.
            InvalidTokenError: если токен не валиден.
        """
        async with self.uow:
            tokens = await self.auth_service.refresh(token)
        return JWTokenDTO(access=tokens.access.token, refresh=tokens.refresh.token)

    async def get_user_by_token(self, token: str) -> UserDTO:
        """
        Raises:
            InvalidTokenError: если токен не валиден.
            ObjectNotFoundError: если пользователь не найден.
        """
        async with self.uow:
            user_id = await self.token_service.get_user_id(token)
            try:
                user = await self.uow.users.get_by_id(user_id)
            except ObjectNotFoundError:
                raise InvalidTokenError("Invalid token. Please, log in again to get a new token")
        return get_dto(user)
