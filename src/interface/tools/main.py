from datetime import datetime

from src.interface.clients.ollama_qwen_llm import OllamaQwen
from src.interface.tools.tool_handler import ToolRegistry, Tool


def get_current_time() -> str:
    """Get the current system time in HH:MM:SS format."""
    return datetime.now().strftime("%H:%M:%S")


tools = ToolRegistry({"get_current_time": Tool(get_current_time)})

llm = OllamaQwen(model="qwen2.5:3b", temperature=0, tools=tools.describe_tools(), tool_choice="auto")

res = llm.chat([
    {"role": "system", "content": "You are a helpful assistant. Do not make up data, use tools when needed."},
    {"role": "user", "content": "List what tools you have."}
])

print({
    "content": res.get("content"),
    "tool_calls": list(
        map(lambda t: f"name: {t.function_name}, args: {t.arguments}, id: {t.id}", res.get("tool_calls"))),
    "is_tool_call": res.get("is_tool_call"),
})
