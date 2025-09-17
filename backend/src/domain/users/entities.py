from dataclasses import dataclass
from typing import Self
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class User:
    id: UUID
    username: str
    password_hash: str
    email: str
    first_name: str
    last_name: str
    is_superuser: bool
    is_active: bool

    @classmethod
    def create(
        cls, username, password_hash, email, first_name, last_name, is_superuser=False, is_active=True
    ) -> Self:
        if not username.strip() or not email.strip() or not password_hash.strip():
            raise ValueError("Username, email and password_hash cannot be empty")
        return User(
            id=uuid4(),
            username=username,
            email=email,
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name,
            is_superuser=is_superuser,
            is_active=is_active,
        )
