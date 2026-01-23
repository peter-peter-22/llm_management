from src.interface2.plan_then_execute_v2.entites import Plan, ProcessedPlan, ProcessedStep


class PlanManager:
    def __init__(self, initial_plan: Plan):
        steps = {step.id: ProcessedStep.model_validate(step.model_dump()) for step in initial_plan.steps}
        self.plan = ProcessedPlan(steps=steps)

    def print_full_plan(self):
        print(self.plan.model_dump_json(indent=4))

    def print_plan_for_replanner(self):
        pass

    def resolve_symbolic_reference(self, ref: str):
        pass
