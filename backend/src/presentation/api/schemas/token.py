from pydantic import BaseModel


class TokenPairSchema(BaseModel):
    access: str
    refresh: str
