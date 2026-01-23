from enum import Enum
from typing import Optional, Any

from pydantic import BaseModel

type StepId = int


class Step(BaseModel):
    id: StepId
    capability: str
    inputs: Optional[dict[str, Any]]
    depends_on: Optional[list[StepId]]
    description: Optional[str]


class Plan(BaseModel):
    steps: list[Step]


class CompletionStatus(Enum):
    PENDING = 1
    COMPLETED = 2


class StepOutputField(BaseModel):
    value: Any
    display: bool


class StepOutput(BaseModel):
    values: dict[str, StepOutputField]


class ProcessedStep(Step):
    outputs: Optional[dict[str, StepOutput]] = None
    status: CompletionStatus = CompletionStatus.PENDING


class ProcessedPlan(BaseModel):
    steps: dict[StepId, ProcessedStep]


class Capability:
    def execute(self, **kwargs: Any) -> StepOutput:
        pass


def _test():
    step = Step(id=1, capability='DB_SCHEMA', inputs={'scope': 'projects'}, depends_on=[],
                description='Get schema for projects table.')
    d = step.model_dump()
    print(ProcessedStep.model_validate(d))


if __name__ == '__main__':
    _test()
