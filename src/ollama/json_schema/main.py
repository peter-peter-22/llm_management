from ollama import chat
from pydantic import BaseModel


class Pet(BaseModel):
    name: str
    animal: str
    age: int
    color: str | None
    favorite_toy: str | None


class PetList(BaseModel):
    pets: list[Pet]


response = chat(
    model='qwen2.5:3b',
    messages=[{'role': 'user', 'content': 'I have two cats named Luna and Loki...'}],
    format=PetList.model_json_schema(),
)

pets = PetList.model_validate_json(response.message.content)
print(pets)
