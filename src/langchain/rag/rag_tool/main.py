from typing import List

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, AIMessage

from src.langchain.langchain_client import *
from src.langchain.rag.rag_tool.tool import search_documents

agent = create_agent(
    llm,
    tools=[search_documents],
    system_prompt="You are a helpful assistant at a company called Fakesoft, have a tool can access the documents of the company."
                  "If you don't know something, use the search tool multiple times, ask the user for more information only if you are sure the context is not within the company documents."
                  "After you are done with searching and thinking, provide your final answer to the user"
)

messages: List[AIMessage] = agent.invoke({
    "messages": [HumanMessage(
        "When did John doe joined fakesoft, what is his position and what is the alternative name of Fakesoft?")]
}).get("messages")

response: AIMessage = messages[-1]
print(response.content)
