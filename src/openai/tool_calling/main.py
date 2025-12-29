import datetime

from src.openai.openai_client import *


def tool_calling(message: str):
    """
        More complex chat with tool calling support.
        Supports a placeholder tool: 'get_current_time' which returns the current time.

        Args:
        messages (list): List of message dictionaries.

        Returns:
        str: The model's final response content after any tool calls.

        Caveats/Limitations:
        - Tool calling requires model support; qwen3:4b might not handle it perfectly (e.g., may not trigger tools reliably).
          Test with prompts like "What time is it?" If it fails, switch to a model like llama3.1:8b.
        - Only one tool call handled per turn for simplicity; real apps may need multi-call loops.
        - No validation on tool parameters (our tool has none); add JSON schema validation for robustness.

        Improvements:
        - Handle multiple tool calls in a loop until no more are needed.
        - Add more tools (e.g., weather API) and dynamic tool selection.
        - For better environments: Consider LangChain or Haystack for chaining tools, agents, and LLMs with Ollama.
          These frameworks handle tool integration, memory, and routing more elegantly than raw OpenAI calls.
        """

    messages = [
        {"role": "system", "content": "You are an AI agent that can call tools, use them when necessary."},
        {"role": "user", "content": message}
    ]

    # Define the placeholder tool
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_current_time",
                "description": "Get the current system time in HH:MM:SS format.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }
    ]

    # Initial call with tools
    response = client.chat.completions.create(
        **model_args,
        messages=messages,
        tools=tools
    )

    message = response.choices[0].message
    if message.tool_calls:
        # Process tool call
        tool_call = message.tool_calls[0]
        print("Tool call:" + tool_call.function.name)
        if tool_call.function.name == "get_current_time":
            tool_result = datetime.datetime.now().strftime("%H:%M:%S")
        else:
            tool_result = "Unknown tool"

        # Append tool response and call again for final answer
        new_messages = messages + [
            message,  # Assistant's message with tool call
            {
                "role": "tool",
                "content": tool_result,
                "tool_call_id": tool_call.id
            }
        ]
        final_response = client.chat.completions.create(
            **model_args,
            messages=new_messages
        )
        return final_response.choices[0].message.content
    else:
        return message.content


print(tool_calling("What is the current time?"))
