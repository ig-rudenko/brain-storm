from fastapi import APIRouter, Depends, HTTPException

from src.application.dialogs.commands import StartDialogCommand
from src.application.dialogs.handlers import DialogHandler
from src.application.users.dto import UserDTO
from src.domain.common.exceptions import ValidationError

from ..auth import get_current_user
from ..dependencies import dialog_handler
from ..schemas.dialogs import CreateDialogSchema, DialogSchema

router = APIRouter(prefix="/dialogs", tags=["dialogs"])


@router.post("", response_model=DialogSchema)
async def create_dialog(
    data: CreateDialogSchema,
    user: UserDTO = Depends(get_current_user),
    handler: DialogHandler = Depends(dialog_handler),
):
    try:
        return await handler.handle_start_dialog(
            user_id=user.id, cmd=StartDialogCommand(name=data.name, pipeline_id=data.pipeline_id)
        )
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
