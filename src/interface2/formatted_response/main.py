from typing import Literal

from pydantic import Field, BaseModel

from src.interface2.clients.ollama_qwen_llm import OllamaModel
from src.interface2.tools.tool_loop import ToolLoop


class Car(BaseModel):
    brand: str = Field(description="The brand of the car. example: 'BMW'", default="unknown")
    model: str = Field(description="The model of the car. example: 'M3 GTR'", default="unknown")
    shape: Literal["sedan", "coupe", "truck", "pickup", "other", "unknown"] = Field(description="The shape of the car",
                                                                                    default="unknown")
    color: str = Field(description="The color of the car. example: 'red'", default="unknown")


llm = OllamaModel(model="qwen2.5:3b", model_args={"temperature": 0})

messages = [
    {"role": "system", "content": "Extract data from the user message by using the response tool."},
    {"role": "user", "content": "I have a blue Volkswagen Polo. I brought it in 2006. It is a sedan."}
]

loop = ToolLoop[Car](llm, response_model=Car, model_args={"tool_choice": "auto"})
res = loop.loop(messages)

print(res.structured_response)
