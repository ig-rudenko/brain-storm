from pydantic import BaseModel


class RegisterUserCommand(BaseModel):
    username: str
    email: str
    password: str
    first_name: str = ""
    last_name: str = ""


class LoginUserCommand(BaseModel):
    username: str
    password: str
