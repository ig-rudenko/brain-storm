from pydantic import BaseModel


class TokenPairSchema(BaseModel):
    access: str
    refresh: str


class OneTokenSchema(BaseModel):
    token: str
