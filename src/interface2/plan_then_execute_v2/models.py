from src.interface2.clients.ollama_qwen_llm import OllamaModel

llm_deterministic = OllamaModel(
    # model="qwen3:4b", # long/infinite thinking
    # model="qwen2.5:3b", # hallucinates SQL without calling DB_SCHEMA
    # model="deepseek-r1:8b-0528-qwen3-q4_K_M", # long/infinite thinking
    model="qwen2.5:7b-instruct",
    # model="huihui_ai/nemotron-v1-abliterated:8b-llama-3.1-nano",
    model_args={
        "temperature": 0.0,
        "top_p": 0.3,
        "top_k": 40
    }
)
