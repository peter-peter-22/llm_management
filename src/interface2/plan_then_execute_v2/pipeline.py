from src.interface2.plan_then_execute_v2.capabilities import DbSchema, DbQuery, Summarize
from src.interface2.plan_then_execute_v2.entites import ProcessedPlan
from src.interface2.plan_then_execute_v2.execution import CapabilityHandler
from src.interface2.plan_then_execute_v2.extract_plan import extract_plan
from src.interface2.plan_then_execute_v2.final_answer import final_answer
from src.interface2.plan_then_execute_v2.plan_manager import PlanManager
from src.interface2.plan_then_execute_v2.planner import create_plan
from src.interface2.plan_then_execute_v2.re_planner import re_plan


# Add CoT
def plan_then_execute(user_prompt: str):
    retries = 3
    executor = CapabilityHandler({
        "DB_SCHEMA": DbSchema(),
        "DB_QUERY": DbQuery(),
        "SUMMARIZE": Summarize()
    })
    manager = PlanManager(create_initial_plan(user_prompt, retries))
    print("Generated initial plan")

    while True:
        print("Execution")
        # Warning: When multiple steps are processed, the error might happen after one output was successfully written
        try:
            executor.execute_plan(manager.plan)
            if manager.plan.check_completion():
                break
        except ValueError as e:
            error = e.__str__()
            print("Error while execution:\n", error)
            for i in range(retries + 1):
                print("Attempting fix")
                new_plan = structured_re_plan(user_prompt, manager.plan, 3, error)
                try:
                    executor.execute_plan(manager.plan)
                    print("Fix successful")
                    manager.apply_replan(new_plan)
                    error = None
                    break
                except ValueError as e:
                    error = e.__str__()
                    print("Error while fixing:\n", error)
                    print(f"Trying again. Attempt {i + 1}/{retries}")
                    continue
            if error:
                raise Exception("No more retries")

        print("Re-planning")
        new_plan = structured_re_plan(user_prompt, manager.plan, 3)
        manager.apply_replan(new_plan)

    print("Plan completed\n", manager.plan.to_json(False))
    """[
    {
        "id": 1,
        "capability": "DB_SCHEMA",
        "description": "Get schema for projects table to understand its structure.",
        "output": {
            "table_schemas": {
                "projects": {
                    "id": "INTEGER",
                    "title": "TEXT",
                    "description": "TEXT",
                    "created_at": "TIMESTAMP"
                }
            }
        },
        "inputs": {
            "scope": "projects"
        },
        "include_in_final_answer": "false"
    },
    {
        "id": 2,
        "capability": "DB_QUERY",
        "description": "Retrieve the titles and descriptions of the three most recent projects.",
        "output": {
            "rows": [
                {
                    "title": "Ball game 2",
                    "description": "The second episode of the ball game series. Same ball, different levels."
                },
                {
                    "title": "AI visual translator",
                    "description": "An AI powered OCR and translator for images."
                },
                {
                    "title": "Company messenger application",
                    "description": "A website for internal discussions of the a company."
                }
            ],
            "row_count": 3,
            "schema": {
                "title": "str",
                "description": "str"
            }
        },
        "inputs": {
            "sql": "SELECT title, description FROM projects ORDER BY created_at DESC LIMIT 3"
        },
        "depends_on": [
            1
        ],
        "include_in_final_answer": "false"
    },
    {
        "id": 3,
        "capability": "SUMMARIZE",
        "description": "Summarize the descriptions of the selected projects.",
        "output": {
            "summaries": [
                "The second episode of the ball game series. Same ball, different levels.",
                "An AI powered OCR and translator for images.",
                "A website for internal discussions of the a company."
            ]
        },
        "inputs": {
            "texts": "2.rows[*].description",
            "max_length": 50
        },
        "depends_on": [
            2
        ],
        "include_in_final_answer": "true"
    }
]"""
    print("Building final answer")
    final = final_answer(user_prompt, manager.plan)
    return final.content


def structured_re_plan(goal: str, plan: ProcessedPlan, retries: int,
                       error: str | None = None):
    for i in range(retries + 1):
        try:
            next_steps: list[int] = []
            for step in plan.steps.values():
                if plan.can_be_executed(step):
                    next_steps.append(step.id)
            res = re_plan(goal, plan.to_json(), next_steps, error)
            plan = extract_plan(res.content)
            return plan
        except ValueError as e:
            print("Error while parsing plan:", e)
            print(f"Trying again. Attempt {i + 1}/{retries}")
    raise Exception("No more retries")


def create_initial_plan(user_prompt: str, retries: int):
    for i in range(retries + 1):
        try:
            res = create_plan(user_prompt)
            plan = extract_plan(res.content)  # add error handling
            return plan
        except ValueError as e:
            print("Error while parsing plan:", e)
            print(f"Trying again. Attempt {i + 1}/{retries}")
    raise Exception("No more retries")


def _test():
    res = plan_then_execute("List the 3 most recent projects of the company, briefly describe their goal.")
    print("Final answer:\n", res)


if __name__ == '__main__':
    _test()
