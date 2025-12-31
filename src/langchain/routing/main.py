from typing import Dict

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph.state import CompiledStateGraph

from src.langchain.langchain_client import llm, simple_llm
from src.langchain.routing.router import classify_query, QueryClass


def debug_classification(message: str):
    res = classify_query(message)
    print("Query:", message, "Class:", res)


debug_classification("Tell me the current time.")
debug_classification("Tell me the main point of the following text:"
                     "The cars were invented in 1850 by Henry Ford in America to make transportation faster."
                     "Ford was pioneering transportation technology by making cars."
                     "We use cars today to travel and to transport heavy weights.")
debug_classification("Tell me the current position of John Doe at our company.")

formatting_agent = create_agent(simple_llm, system_prompt="You are a helpful assistant who formats text.")
thinking_agent = create_agent(llm, system_prompt="You are a helpful assistant at a company.")

agent_dict: Dict[QueryClass, CompiledStateGraph] = {
    "formatting": formatting_agent,
    "thinking": thinking_agent
}


def routed_query(message: str):
    agent_name = classify_query(message)
    print("Agent:", agent_name)
    agent = agent_dict[agent_name]
    response: AIMessage = agent.invoke({
        "messages": [HumanMessage(message)]
    }).get("messages")[-1]
    return response.text


print(routed_query("Tell me the main point of the following text, only a few words:"
                   "The cars were invented in 1850 by Henry Ford in America to make transportation faster."
                   "Ford was pioneering transportation technology by making cars."
                   "We use cars today to travel and to transport heavy weights."
                   "The cars replaced horses because they don't eat."
                   "We use cars today to travel and to transport heavy weights."))

print(routed_query(
    "Extract the name of the mentioned product or service from the following text, respond only with the name (if any):"
    "I recently used the AI-image-generator-321 website, it is awesome, it can generate images from text."
    "I used it to make a car that has feet instead of wheels."))
