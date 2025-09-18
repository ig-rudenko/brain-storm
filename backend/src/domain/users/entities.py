from dataclasses import dataclass, field
from datetime import datetime
from typing import Self
from uuid import UUID, uuid4

from src.domain.common.exceptions import ValidationError


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

    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    @classmethod
    def create(
        cls,
        username: str,
        password_hash: str,
        email: str,
        first_name: str,
        last_name: str,
        is_superuser=False,
        is_active=True,
    ) -> Self:
        username = username.strip()
        email = email.strip()
        password_hash = password_hash.strip()
        if not username or not email or not password_hash:
            raise ValidationError("Username, email and password_hash cannot be empty")
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
