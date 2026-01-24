import json
from enum import Enum
from typing import Optional, Any

from pydantic import BaseModel

type StepId = int


class Step(BaseModel):
    id: StepId
    capability: str
    inputs: Optional[dict[str, Any]]
    depends_on: Optional[list[StepId]] = None
    description: Optional[str] = None
    include_in_final_answer: bool = False


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

    def to_dict_cleaned(self, hidden_text: str):
        """Cleaned dict for presenting the outputs for the re-planner."""
        return {
            k: v.value if v.display else hidden_text
            for k, v in self.values.items()
        }

    def to_dict(self):
        return {
            k: v.value
            for k, v in self.values.items()
        }


class ProcessedStep(Step):
    outputs: StepOutput | None = None
    status: CompletionStatus = CompletionStatus.PENDING

    def to_dict(self, clean: bool = True) -> dict[str, Any]:
        """Cleaned dict for presenting the step for the re-planner."""
        d: dict[str, Any] = {
            "id": self.id,
            "capability": self.capability,
            "description": self.description,
            "include_in_final_answer": self.include_in_final_answer,
            "inputs": self.inputs,
        }
        if self.outputs:  d["output"] = self.outputs.to_dict_cleaned(
            "@" + str(self.id)) if clean else self.outputs.to_dict()
        if self.depends_on:  d["depends_on"] = self.depends_on
        if self.status == CompletionStatus.COMPLETED: d["completed"] = True
        return d


class ProcessedPlan(BaseModel):
    steps: dict[StepId, ProcessedStep]

    def to_dict(self, clean: bool = True):
        return [
            v.to_dict(clean)
            for k, v in self.steps.items()
        ]

    def to_json(self, clean: bool = True):
        """Cleaned JSON for presenting the plan for the re-planner."""
        return json.dumps(self.to_dict(clean), indent=4)

    def check_completion(self):
        """Return true if all steps are completed"""
        for step in self.steps.values():
            if step.status != CompletionStatus.COMPLETED:
                return False
        return True

    def can_be_executed(self, step: ProcessedStep):
        # Skip if completed
        if step.status == CompletionStatus.COMPLETED:
            return False
        # Execute if no dependencies
        if step.depends_on is None:
            return True
        # Skip if not all the dependencies are completed, otherwise execute
        for dep_id in step.depends_on:
            dep = self.steps.get(dep_id)
            if dep is None:
                raise ValueError(f"Step {step.id} depends on step {dep_id}, but no step has this id.")
            if dep.status != CompletionStatus.COMPLETED:
                return False
        return True

    def get_completed_steps(self):
        s: list[int] = []
        for step in self.steps.values():
            if step.status == CompletionStatus.COMPLETED:
                s.append(step.id)
        return s


class ExecutionContext:
    def __init__(self, plan: ProcessedPlan):
        self.plan = plan


class Capability:
    def execute(self, ctx: ExecutionContext, **kwargs: Any) -> StepOutput:
        pass


def _test():
    pass


if __name__ == '__main__':
    _test()
