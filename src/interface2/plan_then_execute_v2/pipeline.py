from src.interface2.plan_then_execute_v2.capabilities import DbSchema, DbQuery, Summarize
from src.interface2.plan_then_execute_v2.executor import CapabilityHandler
from src.interface2.plan_then_execute_v2.extract_plan import extract_plan
from src.interface2.plan_then_execute_v2.planner import create_plan
from src.interface2.plan_then_execute_v2.types import ProcessedStep, CompletionStatus


def plan_then_execute(user_prompt: str):
    executor = CapabilityHandler({
        "DB_SCHEMA": DbSchema(),
        "DB_QUERY": DbQuery(),
        "SUMMARIZE": Summarize()
    })
    p_plan = create_initial_plan(user_prompt)


def create_initial_plan(user_prompt: str):
    res = create_plan(user_prompt)
    plan = extract_plan(res)  # add error handling
    p_plan = [ProcessedStep.model_construct(**step, status=CompletionStatus.PENDING) for step in plan.steps]
    return p_plan
