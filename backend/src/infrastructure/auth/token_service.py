from dataclasses import dataclass
from typing import Literal
from uuid import UUID

import jwt
from datetime import datetime, timedelta, UTC


@dataclass(frozen=True, slots=True)
class TokenPair:
    access: str
    refresh: str


type token_type = Literal["access", "refresh"]


class JWTService:
    def __init__(self, secret: str, access_expiration_minutes: int = 60, refresh_expiration_days: int = 30):
        self.secret = secret
        self.access_expiration_minutes = access_expiration_minutes
        self.refresh_expiration_days = refresh_expiration_days

    def create_token_pair(self, user_id: str) -> TokenPair:
        return TokenPair(
            access=self._create_token(user_id, "access"),
            refresh=self._create_token(user_id, "refresh"),
        )

    def get_user_id(self, token: str, type_: token_type) -> UUID:
        data = jwt.decode(token, self.secret, algorithms=["HS256"])
        if data["exp"] < datetime.now(UTC):
            raise ValueError("Token expired. Please log in again to obtain a new one.")
        if not data["sub"] or not str(data["sub"]).isdigit():
            raise ValueError("Token does not contain a user ID. Please log in again to obtain a new one.")
        if data["type"] != type_:
            raise ValueError(
                "Token does not contain the correct type. Please log in again to obtain a new one."
            )
        return UUID(f"urn:uuid:{data["sub"]}")

    def _create_token(self, user_id: str, type_: token_type) -> str:
        if type_ == "access":
            delta = timedelta(minutes=self.access_expiration_minutes)
        else:
            delta = timedelta(days=self.refresh_expiration_days)

        payload = {
            "sub": user_id,
            "exp": datetime.now(UTC) + delta,
            "type": type_,
        }
        return jwt.encode(payload, self.secret, algorithm="HS256")
