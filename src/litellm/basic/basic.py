from litellm import completion

from src.litellm.common import model_args

response = completion(
    **model_args,
    messages=[{"role": "user", "content": "Hello!"}]
)

print(response.choices[0].message.content)
