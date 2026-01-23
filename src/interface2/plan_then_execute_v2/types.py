from enum import Enum
from typing import Optional, Any

from pydantic import BaseModel


class Step(BaseModel):
    id: int
    capability: str
    inputs: Optional[dict[str, Any]]
    depends_on: Optional[list[int]]
    description: Optional[str]


class Plan(BaseModel):
    steps: list[Step]


class CompletionStatus(Enum):
    PENDING = 1
    COMPLETED = 3


class StepOutputField(BaseModel):
    value: Any
    display: bool


class StepOutput(BaseModel):
    outputs: dict[str, StepOutputField]


class ProcessedStep(Step):
    outputs: Optional[dict[str, StepOutput]] = None
    status: CompletionStatus = CompletionStatus.PENDING


class ProcessedPlan(BaseModel):
    steps: dict[int, ProcessedStep]


class Capability:
    def execute(self, args: dict[str, Any] | None) -> StepOutput:
        pass
