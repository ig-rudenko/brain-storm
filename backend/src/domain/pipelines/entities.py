from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Literal, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class AgentNode(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    type: Literal["agent"]
    agent_id: UUID


class SequenceNode(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    type: Literal["sequence"]
    nodes: List["Node"]


class MergeStrategy(str, Enum):
    CONCAT = "concat"
    CONCAT_NUMBERED = "concat_numbered"


class ParallelNode(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    type: Literal["parallel"]
    merge_strategy: MergeStrategy
    nodes: List["Node"]


class TransformNode(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    type: Literal["transform"]
    config: Dict[str, Any] = {}


Node = Union[AgentNode, SequenceNode, ParallelNode, TransformNode]
SequenceNode.model_rebuild()
ParallelNode.model_rebuild()


class Pipeline(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    root: Node
