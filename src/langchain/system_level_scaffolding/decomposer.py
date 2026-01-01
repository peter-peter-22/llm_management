from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from src.langchain.langchain_client import llm
from src.langchain.system_level_scaffolding.database.tools import tools


class Plan(BaseModel):
    """The sketch of the plan"""
    goal: str = Field(description="Brief summary about the goal")
    steps: list[str] = Field(description="The steps of the plan")


system_prompt = SystemMessage(
    f"""You are a task decomposer at a tech company 'Fakesoft'.
You must decompose the task the user gives you into a plan and executable and verifiable steps.

Rules:
-You cannot use the tools.
-You must not invent data.
-Only respond with execution steps.
-You plan only using the available tools.

Tool list:
{"\n".join(
        f"""{{
    'name': '{tool.name}',
    'description': '{tool.description}',
    'args': '{tool.args}',
    'returns': '{tool.response_format}'
}}"""
        for tool in tools)}"""
)

print(system_prompt.text)

planner_agent = create_agent(
    model=llm,
    response_format=Plan,  # Auto-selects ProviderStrategy
    system_prompt=system_prompt,
    debug=True
)

result = planner_agent.invoke({
    "messages": [HumanMessage(
        "List the 3 latest projects of the company, briefly describe their goal.")]
})

print(result["structured_response"])
