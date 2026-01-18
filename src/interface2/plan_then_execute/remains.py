from typing import Literal

from pydantic import BaseModel, Field

from src.interface2.clients.ollama_qwen_llm import OllamaModel
from src.interface2.tools.tool_handler import Tool


class GetProjectsArgs(BaseModel):
    limit: int = Field(description="The maximum count of projects to return", default=5)
    sort: Literal["created_at", "title"] = Field(description="Field to order by", default="created_at")
    sort_direction: Literal["ascending", "descending"] = Field(description="Ordering method", default="ascending")


tools = [
    Tool(
        lambda x: x,
        "get_projects",
        """Retrieve a number of projects from the database with adjustable sorting.""",
        GetProjectsArgs
    )
]

llm = OllamaModel(model="qwen2.5:3b", model_args={"temperature": 0})


class PlanStep(BaseModel):
    """One step of the plan"""
    goal: str = Field(description="The goal of this step")
    details: str = Field(description="A detailed description of this task")
    reason: str = Field(description="Why is this step necessary?")


class Steps(BaseModel):
    """Executable steps of the plan"""
    steps: list[PlanStep] = Field(description="The steps of the plan")


class Verification(BaseModel):
    valid: bool = Field(description="Whether or not the plan is valid")
    errors: list[str] = Field(description="A list of errors if any")
    fixes: list[str] = Field(description="A list of fixes if any")


requirements_system_prompt = """List the verifiable requirements of completing the user prompt.
The listed requirements will be forwarded to agents those understand them.

Rules:
-Respond with a list of requirements.
-Do not respond with data.
-Extract the requirements only from the user prompt, do not speculate.
-One requirement can contain only one step.
"""

planner_system_prompt = """You are a planner agent at a tech company 'Fakesoft'.
You must create a plan to complete the user prompt into executable and verifiable steps.
At the end of the plan, include a step for presenting a final answer to the user.

The execution steps will be forwarded to agents with the following capabilities:
-Query the SQL database of Fakesoft for internal information with various filters and limits.
-Semantically transform texts.

Rules:
-Only respond with execution steps.
-Think with the capabilities of the executing agents.
-You must not invent data.
-In each step, include the required actions, the expected output or effect, the required inputs.
"""

verifier_system_prompt = """You are a plan verifying agent at a tech company 'Fakesoft'.
You recently created a plan to complete the user prompt.
Verify if the plan is correct, look for mistakes and inaccuracies.

Rules:
-You cannot use the tools.
-Check if the functions and their parameters are used correctly.
-Check if the plan will complete all requirements of the user prompt.

The tools:
"""

plan_formatter_system_prompt = """You will be provided with a plan for completing a task.
    Extract the steps of this plan.

    Rules:
    -Always use the defined structure for your response.
    -Create executable steps.
    -Do not skip parts of the plan.
    -A step can contain one tool usage or multiple semantic processing.
    -Do not invent data or steps.
    """


def create_plan(message: str):
    messages = [
        {"role": "system", "content": planner_system_prompt},
        {"role": "user", "content": message}
    ]
    plan_semantic = llm.chat(messages)
    print(plan_semantic.content)


create_plan("List the 3 most recent projects of the company, briefly describe their goal.")
