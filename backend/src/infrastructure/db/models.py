from uuid import UUID

from advanced_alchemy.base import UUIDAuditBase, orm_registry
from sqlalchemy import String, func, Text, ForeignKey, Column, Table, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship


class UserModel(UUIDAuditBase):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(150), unique=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password: Mapped[str] = mapped_column(String(150))

    first_name: Mapped[str] = mapped_column(String(150))
    last_name: Mapped[str] = mapped_column(String(150))
    is_superuser: Mapped[bool] = mapped_column(server_default=func.false())
    is_active: Mapped[bool] = mapped_column(server_default=func.true())

    def __repr__(self):
        return f"<User {self.username}>"

    def __str__(self):
        return self.username


agents_conversations_model = Table(
    "agents_conversations",
    orm_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("agent_id", ForeignKey("agents.id", ondelete="RESTRICT")),
    Column("conversation_id", ForeignKey("conversations.id", ondelete="RESTRICT")),
)


class AgentModel(UUIDAuditBase):
    __tablename__ = "agents"
    name: Mapped[str] = mapped_column(String(150))
    temperature: Mapped[float] = mapped_column(default=0.7)
    description: Mapped[str] = mapped_column(Text)
    prompt: Mapped[str] = mapped_column(Text)

    conversations: Mapped[list["ConversationModel"]] = relationship(
        lazy="selectin",
        back_populates="agents",
    )


class ConversationModel(UUIDAuditBase):
    __tablename__ = "conversations"
    name: Mapped[str] = mapped_column(String(150))
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))

    user: Mapped[UserModel] = relationship(
        lazy="joined", back_populates="conversations", innerjoin=True, viewonly=True
    )
    agents: Mapped[list["AgentModel"]] = relationship(
        secondary=agents_conversations_model,
        lazy="selectin",
        back_populates="conversations",
    )


class MessageModel(UUIDAuditBase):
    text: Mapped[str] = mapped_column(Text)

    conversation_id: Mapped[UUID] = mapped_column(ForeignKey("conversations.id", ondelete="RESTRICT"))
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    agent_id: Mapped[UUID] = mapped_column(ForeignKey("agents.id", ondelete="RESTRICT"), nullable=True)

    user: Mapped["UserModel"] = relationship(
        lazy="joined", back_populates="conversations", innerjoin=True, viewonly=True
    )
    agent: Mapped["AgentModel"] = relationship(
        lazy="joined", back_populates="conversations", innerjoin=True, viewonly=True
    )
