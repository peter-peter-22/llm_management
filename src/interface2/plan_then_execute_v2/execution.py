from typing import Optional, Any

from pydantic import ValidationError

from src.interface2.plan_then_execute_v2.capabilities import DbSchema, DbQuery, Summarize
from src.interface2.plan_then_execute_v2.entites import CompletionStatus, ProcessedPlan, ProcessedStep, Capability, \
    StepOutput, ExecutionContext, StepOutputField
from src.interface2.plan_then_execute_v2.error_handling import pretty_pydantic_error
from src.interface2.plan_then_execute_v2.extract_plan import extract_plan
from src.interface2.plan_then_execute_v2.plan_manager import PlanManager


class CapabilityHandler:
    def __init__(self, capabilities: dict[str, Capability]):
        self.capabilities = capabilities

    def execute_capability(self, name: str, args: Optional[dict[str, Any]], ctx: ExecutionContext) -> StepOutput:
        capability = self.capabilities[name]
        if capability is None:
            raise ValueError(f"Unknown capability: {name}")
        return capability.execute(ctx, **args)

    def execute_plan(self, plan: ProcessedPlan):
        """Find and execute the next steps, return the array of the completed ids."""
        # Find the executable steps
        next_steps: list[ProcessedStep] = []
        for step in plan.steps.values():
            if plan.can_be_executed(step):
                next_steps.append(step)
        # Execute
        ctx = ExecutionContext(plan)
        for step in next_steps:
            try:
                try:
                    output = self.execute_capability(step.capability, step.inputs, ctx)
                    print(f"Result of step {step.id}:", output.to_dict())
                    step.outputs = output
                    step.status = CompletionStatus.COMPLETED
                except ValidationError as e:
                    raise ValueError(pretty_pydantic_error(e))
            except ValueError as e:
                raise ValueError(f"Error while executing step {step.id}: {e}")
        return [step.id for step in next_steps]


if __name__ == '__main__':
    executor = CapabilityHandler({
        "DB_SCHEMA": DbSchema(),
        "DB_QUERY": DbQuery(),
        "SUMMARIZE": Summarize()
    })

    print("Full first step")
    plan_t = """[
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
    e_plan = extract_plan(plan_t)
    plan_manager = PlanManager(e_plan)
    executor.execute_plan(plan_manager.plan)

    print("Query only")
    p_plan = ProcessedPlan(steps={
        1: ProcessedStep(
            id=1,
            capability="DB_QUERY",
            inputs={
                "sql": "SELECT * FROM projects ORDER BY created_at DESC LIMIT 3;"
            },
        )
    })
    executor.execute_plan(p_plan)

    print("Summarize")
    p_plan = ProcessedPlan(steps={
        1: ProcessedStep(
            id=1,
            capability="DB_QUERY",
            inputs={
                "sql": "SELECT * FROM projects ORDER BY created_at DESC LIMIT 3;"
            },
            outputs=StepOutput(values={
                "rows": StepOutputField(value=[
                    {"id": 1, "description": "description"},
                    {"id": 2, "description": "description"}
                ], display=False)
            }),
            status=CompletionStatus.COMPLETED
        ),
        2: ProcessedStep(
            id=1,
            capability="SUMMARIZE",
            inputs={
                "texts": "@1.description",
                "max_length": 50
            },
            depends_on=[1]
        )
    })
    executor.execute_plan(p_plan)

    print("Error")
    try:
        print("Query only")
        p_plan = ProcessedPlan(steps={
            1: ProcessedStep(
                id=1,
                capability="DB_QUERY",
                inputs={},
            )
        })
        executor.execute_plan(p_plan)
    except ValueError as e:
        print(e)
