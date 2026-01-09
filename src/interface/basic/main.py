from src.interface.clients.ollama_qwen_llm import OllamaQwen

llm = OllamaQwen(model="qwen2.5:3b", temperature=0)

res = llm.chat([{"role": "user", "content": "Hello"}])

print(res.get("content"))
