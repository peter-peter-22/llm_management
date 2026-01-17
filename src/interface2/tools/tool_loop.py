from typing import Any

from src.interface2.clients.llm_handler import LlmHandler
from src.interface2.tools.tool_handler import ToolRegistry


class ToolLoop:
    def __init__(
            self,
            model: LlmHandler,
            tool_registry: ToolRegistry,
            retries: int = 1,
            max_steps: int = 5
    ):
        self.model = model
        self.tool_registry = tool_registry
        self.retries = retries
        self.max_steps = max_steps

    def loop(self, messages: list[dict[str, Any]]):
        remaining_retries = self.retries
        remaining_steps = self.max_steps
        while remaining_retries >= 0 and remaining_steps >= 0:
            res = self.model.chat(messages)
            if res.is_tool_call:
                print(f"Executing {len(res.tool_calls)} tool call(s).")
                for tool_call in res.tool_calls:
                    print(f"Function: {tool_call.function_name}, Args: {tool_call.arguments}")
                    (tool_res, error) = self.tool_registry.use_tool(tool_call.function_name, tool_call.arguments)
                    if not error:
                        messages.append(tool_res)
                        remaining_retries = self.retries
                    else:
                        messages.append(tool_res)
                        remaining_retries -= 1
                    remaining_steps -= 1
            else:
                return res
        raise Exception("No more retries left")
