from src.interface2.plan_then_execute_v2.planner import Step, Plan


def execute_step(step: Step):
    pass


def execute_plan(plan: Plan):
    for step in plan.steps:
        if step.status == "completed":
            continue
        if step.status == "pending":
            execute_step(step)  # build and describe output
        if step.status == "blocked":
            break


if __name__ == '__main__':
    "{'steps': [{'capability': 'DB_SCHEMA', 'id': 1, 'inputs': {'scope': 'projects'}, 'status': 'completed'}]}"
    example = Plan(steps=[Step(id=1, capability='DB_SCHEMA', inputs={'scope': 'projects'}, status='completed')])
    execute_plan(example)
