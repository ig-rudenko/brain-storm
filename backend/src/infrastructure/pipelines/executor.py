import asyncio
from uuid import UUID

from src.application.agents.handlers import AgentRunner
from src.application.services import AgentLLMClient
from src.domain.agents.entities import Agent
from src.domain.messages.entities import Message, AuthorType
from src.domain.pipelines.entities import Pipeline, Node, TransformNode


class PipelineExecutor:
    def __init__(self, pipeline: Pipeline, dialog_id: UUID, agents: list[Agent], llm_client: AgentLLMClient):
        self.pipeline = pipeline
        self.dialog_id = dialog_id
        self.agents: dict[UUID, AgentRunner] = {
            agent.id: AgentRunner(agent, llm_client=llm_client, dialog_id=dialog_id) for agent in agents
        }
        self.llm_client = llm_client

    async def run(self, user_id: UUID, user_input: str, history: list[Message]) -> list[Message]:
        # Сохраняем сообщение пользователя
        user_msg = Message.from_user(dialog_id=self.dialog_id, text=user_input, user_id=user_id)
        history.append(user_msg)

        # Прокидываем историю в рекурсивную обработку
        new_messages = await self._run_node(self.pipeline.root, history)
        return new_messages

    async def _run_node(
        self, node: Node, messages: list[Message], extra_messages: list[Message] | None = None
    ) -> list[Message]:
        if node.type == "agent":
            print(f"Running agent {node.agent_id}...")
            agent = self.agents[node.agent_id]
            messages_for_agent = [
                msg
                for msg in messages
                if msg.author_type == AuthorType.USER or msg.author_id == agent.agent_id
            ]
            if extra_messages:
                messages_for_agent.extend(extra_messages)

            agent_msg = await agent.run(messages_for_agent)
            return [agent_msg]

        elif hasattr(node, "nodes"):  # SequenceNode или ParallelNode
            if node.type == "sequence":  # Передаем результат предыдущего узла в следующий
                print(f"Running sequence node {node.id}...")
                answer_msgs: list[Message] = []
                for child in node.nodes:
                    answer_msgs.extend(await self._run_node(child, messages, answer_msgs))
                return answer_msgs

            elif node.type == "parallel":
                print(f"Running parallel node {node.id}...")
                tasks = [self._run_node(child, messages, extra_messages) for child in node.nodes]
                results: list[list[Message]] = await asyncio.gather(*tasks)
                agent_msgs = []
                for result in results:
                    agent_msgs.extend(result)
                return [self._merge(agent_msgs, node.merge_strategy)]
        return []

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
                text="\n\n".join(msg.text for msg in results),
            )
        if strategy == "concat_numbered":
            text = ""
            for i, msg in enumerate(results):
                text += f"{i + 1}. {msg.text}\n\n"
            return Message.from_agent(
                dialog_id=results[0].dialog_id,
                agent_id=results[0].author_id,
                text=text.strip(),
            )
        elif strategy == "first":
            return results[0]
        elif strategy == "last":
            return results[-1]
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
