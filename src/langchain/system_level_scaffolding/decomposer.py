from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from src.langchain.langchain_client import llm


class PlanStep(BaseModel):
    """One step of the plan"""
    goal: str = Field(description="The goal of this step")
    details: str = Field(description="A detailed description of this task")
    reason: str = Field(description="Why is this step necessary?")


class Plan(BaseModel):
    """The sketch of the plan"""
    goal: str = Field(description="Brief summary about the goal")
    steps: list[PlanStep] = Field(description="The steps of the plan")


system_prompt = SystemMessage(
    """You are a task decomposer at a tech company 'Fakesoft'.
You must create a plan to complete the user prompt into executable and verifiable steps.
At the end of the plan, present the final answer to the user.

Rules:
-You cannot use tools
-You must not invent data.
-Only respond with execution steps.
-You plan only using the available tools and semantic transformations.
-Do not make up behaviour for the tools, think with their accurate arguments and response.
-Never make a step about retrieving all data from a domain and filtering later, mention the ordering, filtering or limiting arguments of these functions instead. 

The tools:
{
    name: 'get_projects',
    description: 'Retrieve a number of projects from the database with adjustable sorting',
    arguments: [
        limit: {type: int, description: 'The maximum count of projects to return', default: 5},
        sort: {type: Literal['created_at', 'title'], description: 'Field to order by', default: 'created_at'},
        sort_direction: {type: Literal['ascending', 'descending'], description: 'Ordering method', default: 'descending'}
    ],
    returns: List[Project(title:str, description:str, created_at:timestamp)]
}
"""
)

planner_agent = create_agent(
    model=llm,
    response_format=Plan,
    system_prompt=system_prompt,
    debug=True
)

result = planner_agent.invoke({
    "messages": [HumanMessage(
        "List the 3 most recent projects of the company, briefly describe their goal.")]
})
print(result["structured_response"])
