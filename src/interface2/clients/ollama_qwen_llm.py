from typing import Any

import ollama

from src.interface2.clients.llm_handler import LlmHandler, AiResponse, ToolCall


class OllamaQwen(LlmHandler):
    def __init__(
            self,
            model: str,
            tools: list[dict[str, Any]] | None = None,
            tool_choice: str | dict[str, Any] | None = None,
            model_config: dict[str, Any] | None = None,
    ):
        super().__init__(tools, tool_choice)
        self.model = model
        self.model_config = model_config

    def chat(self, messages: list[dict[str, Any]], **kwargs) -> AiResponse:
        res = ollama.chat(
            model=self.model,
            messages=messages,
            tools=self.tools,
            options={
                "tool_choice": self.tool_choice,
                **self.model_config
            },
        )

        message = AiResponse(
            res.message,
            res.message.content,
            len(res.message.tool_calls) > 0 if res.message.tool_calls is not None else False,
            list(map(
                lambda t: ToolCall(
                    t.function.name,
                    t.function.arguments
                ),
                res.message.tool_calls
            )) if res.message.tool_calls else None,
        )
        return message
