from src.interface2.plan_then_execute_v2.types import Plan, ProcessedPlan


class PlanManager:
    def __init__(self, initial_plan: Plan):
        b = {"steps": {step.id: step for step in initial_plan.steps}}
        self.plan = ProcessedPlan.model_validate({"steps": {step.id: step for step in initial_plan.steps}})
