from src.interface2.plan_then_execute_v2.entites import Plan, ProcessedPlan, ProcessedStep, CompletionStatus


# Add a behavior
class PlanManager:
    def __init__(self, initial_plan: Plan):
        steps = {step.id: ProcessedStep.model_validate(step.model_dump()) for step in initial_plan.steps}
        self.plan = ProcessedPlan(steps=steps)

    # Does not check for plan resets
    def apply_replan(self, new_plan: Plan):
        """Apply the changes to the new plan while keeping track of the progress"""
        for new_step in new_plan.steps:
            old_step = self.plan.steps.get(new_step.id)
            if old_step is None:
                self.plan.steps[new_step.id] = ProcessedStep.model_validate(new_step.model_dump())
            else:
                # Completed steps cannot be overwritten
                if old_step.status == CompletionStatus.COMPLETED:
                    continue
                self.plan.steps[new_step.id] = ProcessedStep.model_validate(new_step.model_dump())
