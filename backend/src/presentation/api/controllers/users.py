from fastapi import APIRouter, HTTPException, Depends
from src.application.users.commands import LoginUserCommand
from src.application.users.handlers import JWTLoginUserHandler
from ..dependencies import get_login_handler
from ..schemas.token import TokenPairSchema

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", response_model=TokenPairSchema)
async def login(cmd: LoginUserCommand, jwt_handler: JWTLoginUserHandler = Depends(get_login_handler)):
    try:
        token_pair = await jwt_handler.handle(cmd)
        return token_pair
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
