from typing import Any
from openai import AsyncOpenAI
from openai.types.shared.chat_model import ChatModel

from src.application.services import AgentLLMClient
from src.domain.messages.entities import Message, AuthorType


class OpenAIChatClient(AgentLLMClient):
    def __init__(self, api_key: str, model: ChatModel):
        self._api_key: str = api_key
        self.model: ChatModel = model
        self.client = AsyncOpenAI(api_key=self._api_key)

    async def generate(self, system_prompt: str, messages: list[Message], **kwargs: Any) -> str:
        context = [{"role": "system", "content": system_prompt}]
        for message in messages:
            if message.author_type == AuthorType.USER:
                context.append({"role": "user", "content": message.text})
            elif message.author_type == AuthorType.AGENT:
                context.append({"role": "assistant", "content": message.text})

        resp = await self.client.chat.completions.create(model=self.model, messages=context, **kwargs)
        return resp.choices[0].message.content.strip()
