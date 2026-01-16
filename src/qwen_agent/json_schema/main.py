from qwen_agent.agents import Assistant

json_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "capital": {"type": "string"},
        "languages": {
            "type": "array",
            "items": {"type": "string"}
        }
    },
    "required": ["name", "capital", "languages"]
}

llm_cfg = {
    'model': 'qwen2.5:3b',
    'model_server': 'http://localhost:11434/v1',
    'api_key': 'EMPTY',

    'generate_cfg': {
        'top_p': 0.8,
        'temperature': 0,
        'response_format': {"type": "json_object"},
        "text_format": json_schema  # doesn't works
    }
}

system_instruction = '''You are a helpful assistant. Always respond with JSON.'''
bot = Assistant(
    llm=llm_cfg,
    system_message=system_instruction
)

messages = [{'role': 'user', 'content': "A red BMW model M3 GTR. It is a coupe."}]
responses = ''
for responses in bot.run(messages=messages):
    pass
print(responses)
