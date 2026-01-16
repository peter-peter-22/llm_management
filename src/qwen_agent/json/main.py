from qwen_agent.agents import Assistant

llm_cfg = {
    'model': 'qwen2.5:3b',
    'model_server': 'http://localhost:11434/v1',
    'api_key': 'EMPTY',

    'generate_cfg': {
        'top_p': 0.8,
        'temperature': 0.7,
        'response_format': {"type": "json_object"}
    }
}

system_instruction = '''You are a helpful assistant. Always respond with JSON.'''
bot = Assistant(
    llm=llm_cfg,
    system_message=system_instruction,
)

messages = [{'role': 'user', 'content': "What color is the sky at different times of the day?"}]
responses = ''
for responses in bot.run(messages=messages):
    pass
print(responses)
