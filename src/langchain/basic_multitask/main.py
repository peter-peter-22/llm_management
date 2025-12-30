from typing import List

from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.messages import HumanMessage, AIMessage

from src.langchain.langchain_client import *
from src.langchain.rag.rag_tool.tool import search_documents


@tool
def get_current_time() -> str:
    """Returns the current time."""
    import datetime
    return datetime.datetime.now().strftime("%H:%M:%S")


@tool
def get_current_temp() -> str:
    """Returns the current temperature."""
    return "20C°"


agent = create_agent(
    llm,
    tools=[search_documents, get_current_temp, get_current_time],
    system_prompt="You are a helpful assistant at a company called Fakesoft."
                  "You have access to tools for obtaining different kinds of informations."
                  "If you don't know something, try to get the missing information with your tools."
                  "Attempt multiple tools and parameters if you can't find something."
                  "If you are sure the necessary data is not available, ask the user for more information."
                  "Decompose the tasks it into smaller steps first, thn process the steps and the present your final answer to the user."
)

messages: List[AIMessage] = agent.invoke({
    "messages": [HumanMessage(
        "When did John Doe joined Fakesoft, what is his position and what is the alternative name of Fakesoft?"
        "Also, what is the current time and temperature?"
    )]
}).get("messages")

response: AIMessage = messages[-1]
print(response.content)
