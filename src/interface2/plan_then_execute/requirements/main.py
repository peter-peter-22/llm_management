from src.interface2.plan_then_execute.requirements.semantic import requirements_text
from src.interface2.plan_then_execute.requirements.structured import requirements_structured


def create_requirements(message: str):
    text = requirements_text(message).content
    print("Requirements (text):", text)
    structured = requirements_structured(text)
    return structured


def _test():
    res = create_requirements("List the 3 most recent projects of the company, briefly describe their goal.")
    print(res)


if __name__ == "__main__":
    _test()
