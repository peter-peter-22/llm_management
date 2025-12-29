from typing import List

from langchain_core.messages import AIMessage, SystemMessage, ToolMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool

from src.langchain.langchain_client import *


@tool
def get_current_time() -> str:
    """Returns the current time."""
    import datetime
    return datetime.datetime.now().strftime("%H:%M:%S")


@tool
def get_current_temp() -> str:
    """Returns the current temperature."""
    return "20C°"


tools = [get_current_time, get_current_temp]
llm_with_tools = llm.bind_tools(tools)

# Custom prompt: Low-level, so we define it manually (system prompt + message history)
prompt = ChatPromptTemplate(
    [
        SystemMessage(content="You are a helpful assistant. Use tools if needed, then provide a final answer."),
        MessagesPlaceholder(variable_name="messages", optional=True),
    ]
)


def execute_tool_calls(message: AIMessage) -> List[ToolMessage]:
    """Execute any tool calls from the AIMessage and return ToolMessages."""
    tool_messages = []
    for tool_call in message.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]

        print("Tool called:", tool_name)

        # Find and call the tool
        tool_to_call = next((t for t in tools if t.name == tool_name), None)
        if tool_to_call:
            result = tool_to_call.invoke(tool_args)
            tool_messages.append(
                ToolMessage(
                    content=str(result),
                    tool_call_id=tool_call["id"],
                    name=tool_name,
                )
            )
        else:
            tool_messages.append(
                ToolMessage(
                    content=f"Error: Tool '{tool_name}' not found.",
                    tool_call_id=tool_call["id"],
                    name=tool_name,
                )
            )
    return tool_messages


def chat_with_tools(message: str, max_iterations: int = 10) -> str:
    messages: List[AIMessage] = [HumanMessage(content=message)]
    iteration = 0
    while iteration < max_iterations:
        # Invoke the chain
        test = prompt.invoke({"messages": messages})
        result = llm_with_tools.invoke(prompt.invoke({"messages": messages}))

        # Append the AI's response to history
        messages.append(result)

        # If no tool calls, return the final content
        if isinstance(result, AIMessage) and not result.tool_calls:
            return result.content

        # Execute tools and append results
        tool_results = execute_tool_calls(result)
        messages.extend(tool_results)

        iteration += 1

    return "Max iterations reached without final answer."


print(chat_with_tools("Tell me the current time and temperature."))
