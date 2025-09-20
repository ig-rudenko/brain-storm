import asyncio
from functools import wraps
from uuid import UUID

from src.application.agents.handlers import AgentRunner
from src.application.services import AgentLLMClient
from src.domain.agents.entities import Agent
from src.domain.messages.entities import AuthorType, Message
from src.domain.pipelines.entities import (
    AgentNode,
    Node,
    ParallelNode,
    Pipeline,
    SequenceNode,
    TransformNode,
)


def set_previous_node_decorator(func):

    @wraps(func)
    def wrapper(self: "PipelineExecutor", node: Node, *args, **kwargs):
        result = func(self, node, *args, **kwargs)
        self.set_previous_node(node)
        return result

    return wrapper


class PipelineExecutor:
    def __init__(
        self, pipeline: Pipeline, *, dialog_id: UUID, agents: list[Agent], llm_client: AgentLLMClient
    ):
        self.pipeline = pipeline
        self.dialog_id = dialog_id
        self.agents: dict[UUID, AgentRunner] = {
            agent.id: AgentRunner(agent, llm_client=llm_client, dialog_id=dialog_id) for agent in agents
        }
        self.llm_client = llm_client
        self.generated_messages: list[Message] = []
        self._previous_node: Node | None = None

    def set_previous_node(self, node: Node):
        if isinstance(node, (AgentNode, SequenceNode, ParallelNode, TransformNode)):
            self._previous_node = node

    async def run(self, user_id: UUID, user_input: str, history: list[Message]) -> list[Message]:
        # Сохраняем сообщение пользователя
        user_msg = Message.from_user(dialog_id=self.dialog_id, text=user_input, user_id=user_id)
        self.generated_messages.append(user_msg)
        history.append(user_msg)

        # Прокидываем историю в рекурсивную обработку
        new_messages = await self._run_node(self.pipeline.root, history)
        return new_messages

    @set_previous_node_decorator
    async def _run_node(
        self, node: Node, messages: list[Message], extra_messages: list[Message] | None = None
    ) -> list[Message]:
        if node.type == "agent" and isinstance(node, AgentNode):
            # Запускаем агента
            return await self._run_agent_node(node, messages, extra_messages)

        elif hasattr(node, "nodes"):  # SequenceNode или ParallelNode
            if node.type == "sequence" and isinstance(node, SequenceNode):
                # Передаем результат предыдущего узла в следующий
                return await self._run_sequence_node(node, messages)

            elif node.type == "parallel" and isinstance(node, ParallelNode):
                return await self._run_parallel_node(node, messages, extra_messages)

        return []

    async def _run_agent_node(
        self, node: AgentNode, messages: list[Message], extra_messages: list[Message] | None = None
    ) -> list[Message]:
        """Запускает агента на выполнение"""

        print(f"Running agent {node.agent_id}...")
        if node.agent_id not in self.agents:
            raise ValueError(f"Agent with id {node.agent_id} not found. Check your pipeline config.")

        agent = self.agents[node.agent_id]

        # Агент видит только свои прошлые сообщения и сообщения пользователя.
        messages_for_agent = [
            msg for msg in messages if msg.author_type == AuthorType.USER or msg.author_id == agent.agent_id
        ]

        if extra_messages:  # Если есть дополнительные сообщения, добавляем их
            messages_for_agent.extend(extra_messages)

        # Из истории достаём сообщения предыдущего узла.
        # Нужно для того, чтобы агент мог видеть свои предыдущие запросы,
        # на основе которых ранее сам генерировал ответы.
        # Используется, если в цепочке есть несколько агентов.
        if self._previous_node is not None:
            messages_for_agent.extend(self._get_previous_node_messages(self._previous_node, messages))

        # Сортируем сообщения по времени в обратном порядке (от новых к старым)
        messages_for_agent = sorted(messages_for_agent, key=lambda msg: msg.created_at, reverse=True)

        agent_msg = await agent.run(messages_for_agent)  # Запускаем агента
        self.generated_messages.append(agent_msg)  # Сохраняем сообщение агента в истории
        return [agent_msg]

    async def _run_sequence_node(self, node: SequenceNode, messages: list[Message]) -> list[Message]:
        print(f"Running sequence node {node.id}...")
        answer_msgs: list[Message] = []
        for child in node.nodes:
            answer_msgs = await self._run_node(child, messages, answer_msgs)
        return answer_msgs

    async def _run_parallel_node(
        self, node: ParallelNode, messages: list[Message], extra_messages: list[Message] | None = None
    ) -> list[Message]:
        print(f"Running parallel node {node.id}...")
        tasks = [self._run_node(child, messages, extra_messages) for child in node.nodes]
        results: list[list[Message]] = await asyncio.gather(*tasks)
        agent_msgs = []
        for result in results:
            agent_msgs.extend(result)
        return [self._merge(agent_msgs, node.merge_strategy)]

    @staticmethod
    def _merge(results: list[Message], strategy: str) -> Message:
        if not results:
            raise ValueError("Merge strategy requires at least one result, but got none.")
        if len(results) == 1:
            return results[0]

        if strategy == "concat" and len(results) > 1:
            return Message.from_agent(
                dialog_id=results[0].dialog_id,
                agent_id=results[0].author_id,
                text="\n\n".join(msg.text for msg in results).strip(),
            )
        if strategy == "concat_numbered" and len(results) > 1:
            text = ""
            for i, msg in enumerate(results):
                text += f"## Вариант {i + 1}.\n{msg.text}\n\n"
            return Message.from_agent(
                dialog_id=results[0].dialog_id,
                agent_id=results[0].author_id,
                text=text.strip(),
            )
        else:
            raise ValueError(f"Unknown merge strategy: {strategy}")

    @staticmethod
    def _transform(node: TransformNode, message: str) -> str:
        op = node.config.get("operation")
        if op == "uppercase":
            return message.upper()
        elif op == "lowercase":
            return message.lower()
        # Можно добавить любые другие трансформации
        return message

    def _get_previous_node_messages(self, previous_node: Node, history: list[Message]) -> list[Message]:
        if previous_node.type == "agent":
            return [
                msg
                for msg in history
                if msg.author_id == previous_node.agent_id and msg.author_type == AuthorType.AGENT
            ]

        if previous_node.type == "parallel":
            messages = []
            for child in previous_node.nodes:
                messages.extend(self._get_previous_node_messages(child, history))

            # Сгруппируем сообщения по агентам
            agent_msgs: dict[UUID, list[Message]] = {}
            for msg in messages:
                if msg.author_type != AuthorType.AGENT:
                    continue
                agent_msgs.setdefault(msg.author_id, []).append(msg)

            # Отсортируем сообщения по времени в обратном порядке
            for agent_id in agent_msgs:
                agent_msgs[agent_id] = sorted(
                    agent_msgs[agent_id], key=lambda msg: msg.created_at, reverse=True
                )

            # Применим merge стратегию для сообщений агентов
            merged_msgs = []

            # Берем минимальное количество сообщений для каждого агента
            min_length = min(len(msgs_) for msgs_ in agent_msgs.values())
            for position in range(min_length):
                messages_for_merge = []
                # Для каждого агента берем сообщение с позицией position
                for msgs_ in agent_msgs.values():
                    messages_for_merge.append(msgs_[position])
                merged_msgs.append(self._merge(messages_for_merge, previous_node.merge_strategy))

            return merged_msgs

        if previous_node.type == "sequence" and previous_node.nodes:
            return self._get_previous_node_messages(previous_node.nodes[-1], history)

        return []
