from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, AIMessage

from src.langchain.langchain_client import *
from src.langchain.rag.middleware import prompt_with_context

agent = create_agent(
    llm,
    tools=[],
    middleware=[prompt_with_context],
    system_prompt="You are a helpful assistant."
)

response: AIMessage = agent.invoke({
    "messages": [HumanMessage("Where John Doe works at?")]
}).get("messages")[-1]
print(response.content)
