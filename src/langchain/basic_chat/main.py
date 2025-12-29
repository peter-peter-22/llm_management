from langchain_core.messages import SystemMessage, HumanMessage

from src.langchain.langchain_client import *

messages = [
    SystemMessage(content="You are a helpful assistant."),
    HumanMessage(content="Briefly describe gravity.")
]

response = llm.invoke(messages)
print(response.content)
