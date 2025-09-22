from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class UserDTO:
    id: UUID
    username: str
    email: str
    first_name: str
    last_name: str

    is_active: bool
    is_superuser: bool

    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class JWTokenDTO:
    access: str
    refresh: str
