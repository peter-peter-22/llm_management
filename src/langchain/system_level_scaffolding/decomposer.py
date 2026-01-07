from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field

from src.langchain.langchain_client import llm

qwen = ChatOllama(model="qwen2.5:3b", temperature=0.0, format="json")


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


tool_descriptions = """{
    name: 'get_projects',
    description: 'Retrieve a number of projects from the database with adjustable sorting',
    arguments: [
        limit: {type: int, description: 'The maximum count of projects to return', default: 5},
        sort: {type: Literal['created_at', 'title'], description: 'Field to order by', default: 'created_at'},
        sort_direction: {type: Literal['ascending', 'descending'], description: 'Ordering method', default: 'descending'}
    ],
    returns: List[Project(title:str, description:str, created_at:timestamp)]
}"""

planner_system_prompt = SystemMessage(
    """You are a task decomposer at a tech company 'Fakesoft'.
You must create a plan to complete the user prompt into executable and verifiable steps.
At the end of the plan, include a step for presenting a final answer to the user.

Rules:
-You cannot use tools, describe their usage in the execution plan.
-You must not invent data.
-Only respond with execution steps.
-You plan only using the available tools and semantic transformations.
-Do not make up behaviour for the tools, think with their accurate arguments and response.
-Never make a step about retrieving all data from a domain and filtering later, mention the ordering, filtering or limiting arguments of these functions instead. 

The tools:
""" + tool_descriptions
)

planner_agent = create_agent(
    model=llm,
    system_prompt=planner_system_prompt,
    debug=True
)

verifier_system_prompt = SystemMessage(
    """You are a plan verifying agent at a tech company 'Fakesoft'.
You recently created a plan to complete the user prompt.
Verify if the plan is correct, look for mistakes and inaccuracies.

Rules:
-You cannot use the tools.
-Check if the functions and their parameters are used correctly.
-Check if the plan will complete all requirements of the user prompt.

The tools:
""" + tool_descriptions
)

verifier_agent = create_agent(
    model=qwen,
    system_prompt=verifier_system_prompt,
    debug=True
)

plan_formatter_system_prompt = SystemMessage(
    """You will be provided with a plan for completing a task.
    Extract the steps of this plan.
    
    Rules:
    -Always use the defined structure for your response.
    -Create executable steps.
    -Do not skip parts of the plan.
    -A step can contain one tool usage or multiple semantic processing.
    -Do not invent data or steps.
    """)

format_plan_agent = create_agent(
    model=llm,
    system_prompt=plan_formatter_system_prompt,
    response_format=Steps,
    debug=True
)


def serialize_plan(plan: Steps):
    t: str = (f"-Goal: '{plan.goal}'"
              f"-Reasoning: '{plan.reasoning}'")
    for i in range(len(plan.steps)):
        step = plan.steps[i]
        t += (f"-Step {i + 1}:"
              f"  -Goal: '{step.goal}'"
              f"  -Reasoning: '{step.reason}'"
              f"  -Details: '{step.details}'")
    return t


def create_plan(message: str):
    plan_semantic: AIMessage = planner_agent.invoke({
        "messages": [HumanMessage(message)]
    }).get("messages")[-1]

    plan: Steps = format_plan_agent.invoke({
        "messages": [HumanMessage(plan_semantic.content)]
    }).get("structured_response")

    print(plan)


create_plan("List the 3 most recent projects of the company, briefly describe their goal.")
