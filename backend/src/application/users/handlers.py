from src.application.users.commands import LoginUserCommand, RegisterUserCommand
from src.application.users.dto import UserDTO
from src.domain.common.unit_of_work import UnitOfWork
from src.domain.users.entities import User
from src.infrastructure.auth.hashers import PasswordHasherProtocol
from src.infrastructure.auth.token_service import JWTService, TokenPair


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

    async def handle_obtain_token(self, cmd: LoginUserCommand) -> TokenPair:
        async with self.uow:
            user = await self.uow.users.get_by_username(cmd.username)
            if user is None or not self.hasher.verify(cmd.password, user.password_hash):
                raise ValueError("Invalid email or password")
            if not user.is_active:
                raise ValueError("User is inactive")

            tokens = self.token_service.create_token_pair(user_id=str(user.id))
            return tokens

    async def handle_refresh_token(self, token: str) -> TokenPair:
        return self.token_service.refresh_token(token)

    async def get_user_by_token(self, token: str) -> UserDTO:
        user_id = self.token_service.get_user_id(token, "access")
        user = await self.uow.users.get_by_id(user_id)
        if user is None:
            raise ValueError("Invalid token. Please, log in again to get a new token")
        return get_dto(user)
