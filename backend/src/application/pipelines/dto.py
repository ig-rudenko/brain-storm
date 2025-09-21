from dataclasses import dataclass
from typing import Any
from uuid import UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class PatchPipelineCommand:
    pipeline_id: UUID
    name: str | None = None
    description: str | None = None
    root: dict[str, Any] | None = None

    def to_dict(self) -> dict:
        return {
            "pipeline_id": self.pipeline_id,
            "name": self.name,
            "description": self.description,
            "root": self.root,
        }
