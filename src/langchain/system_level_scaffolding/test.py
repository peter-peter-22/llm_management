from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field

from src.langchain.langchain_client import *


class Output(BaseModel):
    is_odd: bool = Field(description="True if the number is odd, otherwise false.")


agent = create_agent(
    model=llm,
    response_format=Output
)


def is_odd(number: int) -> bool:
    result: Output = agent.invoke({
        "messages": [
            HumanMessage("Is the number {number} odd?".format(number=number))
        ]
    })["structured_response"]

    return result.is_odd


for i in range(1, 10):
    print(i, is_odd(i))
