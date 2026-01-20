from src.interface2.plan_then_execute.planning.main import create_plan, create_plan_fix
from src.interface2.plan_then_execute.planning.split import PlanSteps
from src.interface2.plan_then_execute.requirements.main import create_requirements
from src.interface2.plan_then_execute.verified_plan.verify import verify_plan, Rating


def create_verified_plan(message: str, max_retries: int = 2):
    req = create_requirements(message).requirements
    plan = create_plan(message)
    check = verify_plan(message, plan, req)
    verification_loop(plan, check, req, message, max_retries)


def verification_loop(plan: PlanSteps, check: Rating, req: list[str], user_input: str, max_retries: int, ):
    remaining_retries = max_retries
    while not check.valid:

        # Handle retry counter
        print("The plan was not correct. Errors:", check.errors)
        if remaining_retries <= 0:
            raise Exception(f"The maximum number of retries has been reached.")
        remaining_retries -= 1

        # Add the failed plan and the errors to the message history
        error_message = "The plan was not correct.\nMissing requirements:\n" + "\n".join(
            ["-" + err for err in check.errors])
        print(error_message)
        plan_text = "\n".join(["-" + step for step in plan.steps])
        plan = create_plan_fix(plan_text, user_input, error_message)

        # Validate the new plan
        check = verify_plan(user_input, plan, req)
    return plan


def _test():
    """Fix a slightly wrong plan"""

    goal = "List the 3 most recent projects of the company, briefly describe their goal."
    steps = [
        'Query the SQL database of Fakesoft for a list of all projects',
        'Present the results from step 1 to a text transformation agent for semantic processing, converting the project descriptions into concise briefs that highlight the main goal or objective of each project.',
        'After receiving the processed briefs from the text transformation agent, present the list of the 3 most recent projects and their brief descriptions to the user as the final answer.'
    ]
    reqs = [
        'Identify the 3 most recent projects of the company.',
        'Briefly describe the goal of each project.'
    ]

    plan = PlanSteps(steps=steps)
    check = verify_plan(goal, steps, reqs)
    res = verification_loop(plan, check, reqs, goal, 2)
    print(res)


if __name__ == "__main__":
    _test()
