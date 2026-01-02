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
    f"""You are a helpful AI agent at a tech company 'Fakesoft'.
You need to solve a step of a larger plan with your given tools.
"""
)

print(system_prompt.text)

planner_agent = create_agent(
    model=llm,
    response_format=tools,
    system_prompt=system_prompt,
    debug=True
)

result = planner_agent.invoke({
    "messages": [HumanMessage(
        "List the 3 latest projects of the company")]
})

print(result["structured_response"])
