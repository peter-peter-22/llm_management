import instructor
from pydantic import BaseModel


class ExtractUser(BaseModel):
    name: str
    age: int


client = instructor.from_provider("ollama/qwen2.5:3b")
resp = client.create(
    response_model=ExtractUser,
    messages=[{"role": "user", "content": "Extract Jason is 25 years old."}],
)
print(resp.name, resp.age)
