from openai import OpenAI

# Configure client to use Ollama
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"  # Required, but ignored by Ollama
)

# Select mode
model_args = {
    "model": "llama3.2:3b",
}
