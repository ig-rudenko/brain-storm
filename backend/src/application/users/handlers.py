from src.domain.users.entities import User
from src.application.users.commands import RegisterUserCommand

from src.domain.common.unit_of_work import UnitOfWork
from src.infrastructure.auth.hashers import PasswordHasherProtocol
from src.infrastructure.auth.token_service import JWTService, TokenPair
from src.application.users.commands import LoginUserCommand


class RegisterUserHandler:
    def __init__(self, uow: UnitOfWork, hasher: PasswordHasherProtocol):
        self.uow = uow
        self.hasher = hasher

    async def handle(self, cmd: RegisterUserCommand) -> User:
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
        return user


class JWTLoginUserHandler:
    def __init__(self, uow: UnitOfWork, hasher: PasswordHasherProtocol, token_service: JWTService):
        self.uow = uow
        self.hasher = hasher
        self.token_service = token_service

    async def handle(self, cmd: LoginUserCommand) -> TokenPair:
        async with self.uow:
            user = await self.uow.users.get_by_username(cmd.username)
            if user is None or not self.hasher.verify(cmd.password, user.password_hash):
                raise ValueError("Invalid email or password")
            if not user.is_active:
                raise ValueError("User is inactive")

            tokens = self.token_service.create_token_pair(user_id=str(user.id))
            return tokens
