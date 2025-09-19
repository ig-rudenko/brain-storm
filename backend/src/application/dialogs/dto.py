from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class DialogDTO:
    id: UUID
    user_id: UUID
    name: str
    pipeline_id: UUID
