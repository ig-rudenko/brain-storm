import asyncio
from typing import Any
from uuid import uuid4

from src.application.services import AgentLLMClient
from src.domain.agents.entities import Agent
from src.domain.messages.entities import Message
from src.domain.pipelines.entities import Pipeline
from src.infrastructure.llm.openai_client import OpenAIChatClient
from src.infrastructure.pipelines.executor import PipelineExecutor
from src.infrastructure.settings import settings

agents = [
    Agent.create(
        "analytic",
        "test-agent-1",
        """
Ты — аналитик и критик. Твоя цель — рассмотреть идею пользователя с точки зрения возможных проблем, слабых мест, рисков и противоречий.

Твои ответы должны быть структурированными, краткими и конкретными: выдели 2–4 возможные трудности или спорные моменты, и предложи хотя бы одно направление для доработки.""",
    ),
    Agent.create(
        "idea_generator",
        "test-agent-2",
        """
Ты — креативный генератор идей. Твоя цель — развить запрос пользователя и предложить несколько перспективных решений.

В ответе сформулируй 2–4 идейных направления, укажи потенциальные преимущества и варианты применения. Старайся смотреть на ситуацию позитивно и искать возможности.""",
    ),
    Agent.create(
        "creative_designer",
        "test-agent-3",
        """
Ты — визионер с очень странным мышлением. Твоя цель — реагировать на запрос пользователя так, как никто другой.

Твои ответы должны быть нестандартными, парадоксальными, иногда абсурдными, но всё же связанными с исходным вопросом.

Используй метафоры, неожиданные сравнения, футуристические или даже фантастические предположения.

Дай 2–3 идеи, которые звучат необычно, но могут натолкнуть на оригинальное решение.""",
    ),
    Agent.create(
        "moderator",
        "test-agent-4",
        """
Ты — модератор и обобщатель. Твоя цель — взять ответы двух экспертов: первый дал критику и риски, второй предложил идеи и решения.

Составь итоговый ответ для пользователя:

выдели основные риски и проблемы,

представь наиболее перспективные идеи,

предложи синтезированный вывод или план действий, который учитывает как сильные, так и слабые стороны.

Итог должен быть понятным, структурированным и полезным для принятия решений.""",
    ),
]

pipeline_mixed = {
    "name": "parallel-then-summary",
    "root": {
        "type": "sequence",
        "nodes": [
            {
                "type": "parallel",
                "merge_strategy": "concat_numbered",
                "nodes": [
                    {"type": "agent", "agent_id": agents[0].id},
                    {"type": "agent", "agent_id": agents[1].id},
                    {"type": "agent", "agent_id": agents[2].id},
                ],
            },
            {"type": "agent", "agent_id": agents[3].id},
        ],
    },
}


class TestAgentLLMClient(AgentLLMClient):

    async def generate(self, system_prompt: str, messages: list[Message], **kwargs: Any) -> str:
        return "New message"


async def test_pipeline():
    executor = PipelineExecutor(
        dialog_id=uuid4(),
        pipeline=Pipeline.model_validate(pipeline_mixed),
        agents=agents,
        llm_client=OpenAIChatClient(
            settings.openai_api_key, settings.openai_model, base_url=settings.openai_base_url
        ),
    )
    messages = await executor.run(
        user_id=uuid4(),
        user_input="Я хочу открыть кафе в центре города, но не знаю, какую концепцию выбрать, чтобы оно выделялось среди конкурентов",
        history=[],
    )

    print("=" * 200)
    print("=" * 200)
    for message in messages:
        print(message.text)
        print("-" * 200)


if __name__ == "__main__":
    asyncio.run(test_pipeline())
