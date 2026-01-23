from src.interface2.plan_then_execute_v2.capabilities import DbSchema, DbQuery, Summarize
from src.interface2.plan_then_execute_v2.executor import CapabilityHandler
from src.interface2.plan_then_execute_v2.extract_plan import extract_plan
from src.interface2.plan_then_execute_v2.plan_manager import PlanManager
from src.interface2.plan_then_execute_v2.planner import create_plan


def plan_then_execute(user_prompt: str):
    executor = CapabilityHandler({
        "DB_SCHEMA": DbSchema(),
        "DB_QUERY": DbQuery(),
        "SUMMARIZE": Summarize()
    })
    manager = PlanManager(create_initial_plan(user_prompt))


def create_initial_plan(user_prompt: str):
    res = create_plan(user_prompt)
    plan = extract_plan(res)  # add error handling
    return plan
