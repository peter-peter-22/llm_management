import random
from typing import Any

import ollama

from src.interface.clients.llm_handler import LlmHandler, ChatMessage, ProcessChat, ToolCall


class OllamaQwen(LlmHandler):
    def __init__(
            self,
            model: str,
            tools: str | None = None,
            tool_choice: str | dict[str, Any] | None = None,
            temperature: float = 0.0
    ):
        super().__init__(self._chat, tools, tool_choice)
        self.temperature = temperature
        self.model = model

    _chat: ProcessChat

    def _chat(self, messages: list[ChatMessage]):
        res = ollama.chat(
            model=self.model,
            messages=messages,
            tools=self.tools,
            options={
                "tool_choice": self.tool_choice,
                "temperature": self.temperature,
            },
        )
        message: ChatMessage = {
            "role": res.message.role,
            "content": res.message.content,
            "original": res,
            "is_tool_call": len(res.message.tool_calls) > 0,
            "tool_calls": list(map(
                lambda t: ToolCall(
                    t.function.name,
                    t.function.arguments,
                    str(random.randint(0, 10000))
                ),
                res.message.tool_calls
            )),
        }
        return message
