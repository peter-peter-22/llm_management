from datetime import datetime

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.tools import tool

from src.langchain.langchain_client import *


@tool
def get_current_time() -> str:
    """Get the current system time in HH:MM:SS format."""
    return datetime.now().strftime("%H:%M:%S")


tools = [get_current_time]

# Create the agent: This binds the LLM, tools, and prompt.
# It handles the reasoning loop internally (observe, call tools, re-prompt until final answer).
agent = create_agent(
    llm,
    tools,
    system_prompt="You are a helpful assistant. Use tools if needed, then provide a final answer.",
    debug=True
)

response: AIMessage = agent.invoke({
    "messages": [HumanMessage("Tell me the current time.")]
}).get("messages")[-1]
print(response.content)
