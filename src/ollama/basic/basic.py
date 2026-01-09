import ollama

model = "qwen2.5:3b"

response = ollama.chat(
    model=model,
    messages=[
        {"role": "system", "content": "You are concise."},
        {"role": "user", "content": "Explain transformers."}
    ],
)

print(response["message"]["content"])
