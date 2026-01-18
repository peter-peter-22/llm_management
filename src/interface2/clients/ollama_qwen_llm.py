from typing import Any, Callable

import ollama

from src.interface2.clients.llm_handler import LlmHandler, AiResponse, ToolCall


class OllamaModel(LlmHandler):
    def __init__(
            self,
            model: str,
            model_args: dict[str, Any] | None = None,
    ):
        super().__init__(model_args)
        self.model = model

    def chat(
            self,
            messages: list[dict[str, Any]],
            tools: list[Callable[..., Any]] | None = None,
            tool_choice: str | dict[str, Any] | None = None,
            model_args: dict[str, Any] | None = None,
    ) -> AiResponse:
        res = ollama.chat(
            model=self.model,
            messages=messages,
            tools=tools,
            options={
                "tool_choice": tool_choice,
                **(self.model_args if self.model_args else {}),
                **(model_args if model_args else {}),
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
