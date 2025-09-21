from uuid import UUID

from pydantic import BaseModel, Field


class CreateUpdateAgentSchema(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    description: str
    prompt: str = Field(..., min_length=2, max_length=1500)
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)


class ReadAgentSchema(CreateUpdateAgentSchema):
    id: UUID

    class Config:
        from_attributes = True


class PatchAgentSchema(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=150)
    description: str | None = Field(default=None)
    prompt: str | None = Field(default=None, min_length=2, max_length=1500)
    temperature: float | None = Field(default=None, ge=0.0, le=1.0)
