from src.interface2.clients.ollama_qwen_llm import OllamaModel

llm = OllamaModel(model="qwen2.5:3b", model_config={"temperature": 0})

res = llm.chat([{"role": "user", "content": "Hello"}])

print(res.get("content"))
