from src.openai.openai_client import *


def basic_chat(message: str):
    """
        Basic chat function using the OpenAI API compatible with Ollama.

        Args:
        messages (list): List of message dictionaries, e.g., [{"role": "user", "content": "Hello!"}]

        Returns:
        str: The model's response content.

        Caveats/Limitations:
        - No error handling here for simplicity; in production, wrap in try-except for API errors.
        - Local models like qwen3:4b may be slow on modest hardware and have limited context (e.g., 4K-8K tokens).
        - Responses can be inconsistent due to model size; larger models yield better coherence.

        Improvements:
        - Add streaming: Set stream=True and iterate over chunks for real-time output.
        - Use temperature=0.7 or other parameters for creativity control.
        """
    response = client.chat.completions.create(
        **model_args,
        messages=[
            {"role": "user", "content": message}
        ],
    )

    return response.choices[0].message.content


print(basic_chat("Explain the concept of gravity in simple terms."))
