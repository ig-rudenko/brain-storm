from dataclasses import dataclass
from uuid import UUID

from src.domain.pipelines.entities import Node


@dataclass(frozen=True, slots=True, kw_only=True)
class PatchPipelineCommand:
    pipeline_id: UUID
    name: str | None = None
    description: str | None = None
    root: Node | None = None

    def to_dict(self) -> dict:
        return {
            "pipeline_id": self.pipeline_id,
            "name": self.name,
            "description": self.description,
            "root": self.root.model_dump() if self.root else None,
        }
