from src.domain.users.entities import User
from src.domain.agents.entities import Agent
from src.domain.conversations.entities import Conversation
from src.domain.messages.entities import Message


def start_conversation(user: User, agents: list[Agent], name: str) -> Conversation:
    """Создать новый разговор между пользователем и агентами."""
    if not user.is_active:
        raise ValueError("Inactive user cannot start conversation")

    if not agents:
        raise ValueError("Conversation must have at least one agent")

    conv = Conversation.create(name=name, user_id=user.id)

    for agent in agents:
        conv.add_agent(agent.id)

    return conv


def send_message(conversation: Conversation, sender: User | Agent, text: str) -> Message:
    """Отправить сообщение от пользователя или агента."""
    if isinstance(sender, User) and not sender.is_active:
        raise ValueError("Inactive user cannot send messages")

    if isinstance(sender, Agent):
        return Message.create(
            conversation_id=conversation.id, text=text, agent_id=sender.id, user_id=conversation.user_id
        )
    else:
        return Message.create(conversation_id=conversation.id, text=text, user_id=sender.id)
