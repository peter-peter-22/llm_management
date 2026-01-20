from src.interface2.plan_then_execute.planning.semantic import plan_text, plan_fix
from src.interface2.plan_then_execute.planning.split import plan_split


def create_plan(message: str):
    text = plan_text(message).content
    print("Plan (text):", text)
    structured = plan_split(text)
    return structured


def create_plan_fix(failed: str, user_input: str, error_message: str):
    text = plan_fix(failed, user_input, error_message).content
    print("Plan (text):", text)
    structured = plan_split(text)
    return structured


def _test():
    res = create_plan("List the 3 most recent projects of the company, briefly describe their goal.")
    print(res)


if __name__ == "__main__":
    _test()
