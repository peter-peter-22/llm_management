from typing import Literal

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field

from src.langchain.langchain_client import *

type QueryClass = Literal["formatting", "thinking"]


class Classification(BaseModel):
    """The result of the classification."""
    query_class: QueryClass = Field(description="The decided class of the message.")


agent = create_agent(
    llm,
    system_prompt="You are a helpful assistant at a company, your job is to classify messages."
                  "Select one from the following classes based on their conditions:"
                  "-'formatting':  Direct text formatting instructions for example summarization, key points."
                  "-'thinking': All other queries.",
    response_format=Classification,
)


def classify_query(query: str) -> QueryClass:
    response: Classification = agent.invoke({
        "messages": [HumanMessage(query)]
    })["structured_response"]
    return response.query_class
