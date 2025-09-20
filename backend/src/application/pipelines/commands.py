from uuid import UUID

from pydantic import BaseModel


class RunPipelineCommand(BaseModel):
    pipeline_id: UUID
    user_id: UUID
    dialog_id: UUID
    user_message: str
