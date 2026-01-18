from src.interface2.plan_then_execute.planning.main import create_plan
from src.interface2.plan_then_execute.requirements.main import create_requirements
from src.interface2.plan_then_execute.verified_plan.verify import verify_plan


def create_verified_plan(message: str):
    plan = create_plan(message)
    req = create_requirements(message)
    check = verify_plan(message, plan, req)
    if check.valid is not "correct":
        raise Exception("invalid plan")
    return plan


def _test():
    res = create_verified_plan("List the 3 most recent projects of the company, briefly describe their goal.")
    print(res)


if __name__ == "__main__":
    _test()
