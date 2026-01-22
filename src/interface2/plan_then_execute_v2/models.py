from src.interface2.clients.ollama_qwen_llm import OllamaModel

llm_deterministic = OllamaModel(
    model="qwen2.5:7b-instruct",
    model_args={
        "temperature": 0.0,
        "top_p": 0.3,
        "top_k": 40
    }
)
