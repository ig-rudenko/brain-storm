from fastapi import APIRouter, Depends, HTTPException

from src.application.users.commands import LoginUserCommand, RegisterUserCommand
from src.application.users.handlers import JWTHandler, RegisterUserHandler
from src.domain.common.exceptions import UniqueError

from ..dependencies import get_register_handler, get_token_auth_handler
from ..schemas.token import TokenPairSchema, OneTokenSchema
from ..schemas.user import RegisterUserSchema, UserSchema

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", response_model=TokenPairSchema)
async def login(cmd: LoginUserCommand, jwt_handler: JWTHandler = Depends(get_token_auth_handler)):
    try:
        token_pair = await jwt_handler.handle_obtain_token(cmd)
        return token_pair
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/token/refresh", response_model=TokenPairSchema)
async def login(token_data: OneTokenSchema, jwt_handler: JWTHandler = Depends(get_token_auth_handler)):
    try:
        token_pair = await jwt_handler.handle_refresh_token(token_data.token)
        return token_pair
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/token/verify", response_model=UserSchema)
async def login(token_data: OneTokenSchema, jwt_handler: JWTHandler = Depends(get_token_auth_handler)):
    try:
        user = await jwt_handler.get_user_by_token(token_data.token)
        return user
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/register", response_model=UserSchema)
async def register(
    data: RegisterUserSchema, register_handler: RegisterUserHandler = Depends(get_register_handler)
):
    try:
        user = await register_handler.handle(
            RegisterUserCommand(
                username=data.username,
                password=data.password,
                email=data.email,
                first_name=data.first_name,
                last_name=data.last_name,
            )
        )
    except UniqueError as exc:
        raise HTTPException(status_code=400, detail=f"User with same {exc.field} already exists") from exc

    return user
