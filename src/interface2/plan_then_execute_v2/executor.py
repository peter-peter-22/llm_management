from typing import Optional, Any

from src.interface2.plan_then_execute_v2.capabilities import DbSchema, DbQuery, Summarize
from src.interface2.plan_then_execute_v2.extract_plan import extract_plan
from src.interface2.plan_then_execute_v2.plan_manager import PlanManager
from src.interface2.plan_then_execute_v2.types import CompletionStatus, ProcessedPlan, ProcessedStep, Capability, \
    StepOutput


class CapabilityHandler:
    def __init__(self, capabilities: dict[str, Capability]):
        self.capabilities = capabilities

    def execute_capability(self, name: str, args: Optional[dict[str, Any]]) -> StepOutput:
        capability = self.capabilities[name]
        if capability is None:
            raise ValueError(f"Unknown capability: {name}")
        return capability.execute(**args)

    def execute_plan(self, plan: ProcessedPlan):
        for step in plan.steps.values():
            if not can_be_executed(step, plan):
                continue
            output = self.execute_capability(step.capability, step.inputs)
            print(output)
            # handle output


def can_be_executed(step: ProcessedStep, plan: ProcessedPlan):
    # Skip if completed
    if step.status == CompletionStatus.COMPLETED:
        return False
    # Execute if no dependencies
    if step.depends_on is None:
        return True
    # Skip if not all the dependencies are completed, otherwise execute
    for dep_id in step.depends_on:
        dep = plan.steps.get(dep_id)
        if dep is None:
            raise ValueError(f"Step {step.id} depends on step {dep_id}, but no step has this id.")
        if dep.status != CompletionStatus.COMPLETED:
            return False
    return True


if __name__ == '__main__':
    plan_text = """[
        {
            "id": "1",
            "capability": "DB_SCHEMA",
            "inputs": {
                "scope": "projects"
            },
            "description": "Get schema for projects table.",
            "depends_on": []
        },
        {
            "id": "2",
            "capability": "DB_QUERY",
            "inputs": {
                "sql": "SELECT * FROM projects ORDER BY start_date DESC LIMIT 3;"
            },
            "description": "Retrieve the 3 most recent project records from the database.",
            "depends_on": ["1"]
        },
        {
            "id": "3",
            "capability": "SUMMARIZE",
            "inputs": {
                "text": "2.rows[*].goal",
                "max_length": 50
            },
            "description": "Summarize the goal of each project.",
            "depends_on": ["2"]
        }
    ]"""
    e_plan = extract_plan(plan_text)
    plan_manager = PlanManager(e_plan)
    executor = CapabilityHandler({
        "DB_SCHEMA": DbSchema(),
        "DB_QUERY": DbQuery(),
        "SUMMARIZE": Summarize()
    })
    executor.execute_plan(plan_manager.plan)
