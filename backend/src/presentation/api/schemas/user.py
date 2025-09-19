from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class RegisterUserSchema(BaseModel):
    username: str
    email: str
    password: str
    first_name: str = ""
    last_name: str = ""


class UserSchema(BaseModel):
    id: UUID
    username: str
    email: str
    first_name: str
    last_name: str
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
