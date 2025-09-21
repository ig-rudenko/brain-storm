from __future__ import annotations

from enum import Enum
from typing import Any, Literal, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, ValidationError


class AgentNode(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    type: Literal["agent"]
    agent_id: UUID


class SequenceNode(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    type: Literal["sequence"]
    nodes: list["Node"]


class MergeStrategy(str, Enum):
    CONCAT = "concat"
    CONCAT_NUMBERED = "concat_numbered"


class ParallelNode(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    type: Literal["parallel"]
    merge_strategy: MergeStrategy
    nodes: list["Node"]


class TransformNode(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    type: Literal["transform"]
    config: dict[str, Any] = {}


Node = Union[AgentNode, SequenceNode, ParallelNode, TransformNode]
SequenceNode.model_rebuild()
ParallelNode.model_rebuild()


class Pipeline(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    description: str = ""
    root: Node

    def get_agent_ids(self) -> list[UUID]:
        return self._get_agents_id(self.root)

    def _get_agents_id(self, node: Node) -> list[UUID]:
        agent_ids: list[UUID] = []
        if node.type == "agent":
            return [node.agent_id]
        elif node.type == "sequence" or node.type == "parallel":
            for node in node.nodes:
                agent_ids.extend(self._get_agents_id(node))
        return agent_ids

    def patch(self, **kwargs):
        """Частичное обновление объекта"""
        if name := kwargs.get("name"):
            self.name = str(name)

        if description := kwargs.get("description"):
            self.description = str(description)

        if root := kwargs.get("root"):
            for node in (AgentNode, SequenceNode, ParallelNode, TransformNode):
                try:
                    self.root = node.model_validate(root)
                    break
                except ValidationError:
                    pass
