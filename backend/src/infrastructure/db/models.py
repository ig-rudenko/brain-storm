from uuid import UUID

from advanced_alchemy.base import UUIDAuditBase, orm_registry
from sqlalchemy import Column, ForeignKey, Integer, String, Table, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.messages.entities import AuthorType


class UserModel(UUIDAuditBase):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(150), unique=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password: Mapped[str] = mapped_column(String(150))

    first_name: Mapped[str] = mapped_column(String(150))
    last_name: Mapped[str] = mapped_column(String(150))
    is_superuser: Mapped[bool] = mapped_column(server_default=func.false())
    is_active: Mapped[bool] = mapped_column(server_default=func.true())

    dialogs: Mapped[list["DialogModel"]] = relationship(back_populates="user", viewonly=True)

    def __repr__(self):
        return f"<User {self.username}>"

    def __str__(self):
        return self.username


agents_dialogs_model = Table(
    "agents_dialogs",
    orm_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("agent_id", ForeignKey("agents.id", ondelete="RESTRICT")),
    Column("dialog_id", ForeignKey("dialogs.id", ondelete="RESTRICT")),
)


class AgentModel(UUIDAuditBase):
    __tablename__ = "agents"
    name: Mapped[str] = mapped_column(String(150))
    temperature: Mapped[float] = mapped_column(default=0.7)
    description: Mapped[str] = mapped_column(Text)
    prompt: Mapped[str] = mapped_column(Text)


class PipelineModel(UUIDAuditBase):
    __tablename__ = "pipelines"
    name: Mapped[str] = mapped_column(String(150))
    description: Mapped[str] = mapped_column(Text)
    definition: Mapped[dict]


class DialogModel(UUIDAuditBase):
    __tablename__ = "dialogs"
    name: Mapped[str] = mapped_column(String(150))
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    pipeline_id: Mapped[UUID] = mapped_column(ForeignKey("pipelines.id", ondelete="RESTRICT"))

    user: Mapped[UserModel] = relationship(back_populates="dialogs", innerjoin=True, viewonly=True)
    messages: Mapped[list["MessageModel"]] = relationship(back_populates="dialog", viewonly=True)


class MessageModel(UUIDAuditBase):
    __tablename__ = "messages"

    text: Mapped[str] = mapped_column(Text)

    dialog_id: Mapped[UUID] = mapped_column(ForeignKey("dialogs.id", ondelete="RESTRICT"))
    author_id: Mapped[UUID]
    author_type: Mapped[AuthorType]
    meta_data: Mapped[dict]

    dialog: Mapped[DialogModel] = relationship(back_populates="messages", innerjoin=True)
