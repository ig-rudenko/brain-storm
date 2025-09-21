from fastapi import APIRouter, Depends, HTTPException

from src.application.pipelines.commands import RunPipelineCommand
from src.application.pipelines.handlers import PipelineHandler
from src.application.users.dto import UserDTO

from ..auth import get_current_user
from ..dependencies import get_pipeline_handler
from ..schemas.message import MessageSchema, MessagesResponseSchema
from ..schemas.pipelines import RunPipelineSchema

router = APIRouter(prefix="", tags=["rpc"])


@router.post("/run-pipeline", response_model=MessagesResponseSchema)
async def run_pipeline(
    data: RunPipelineSchema,
    user: UserDTO = Depends(get_current_user),
    pipeline_handler: PipelineHandler = Depends(get_pipeline_handler),
):
    try:
        messages = await pipeline_handler.handle_run_pipeline(
            RunPipelineCommand(
                pipeline_id=data.pipeline_id,
                dialog_id=data.dialog_id,
                user_id=user.id,
                user_message=data.message,
            )
        )
        return MessagesResponseSchema(result=[MessageSchema.model_validate(msg) for msg in messages])
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
