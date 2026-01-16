from qwen_agent.agents import Assistant

llm_cfg = {
    'model': 'qwen2.5:3b',
    'model_server': 'http://localhost:11434/v1',
    'api_key': 'EMPTY',

    'generate_cfg': {
        'top_p': 0.8,
        'temperature': 0.7,
        'max_tokens': 2048,
    }
}

system_instruction = '''You are a helpful assistant.'''
bot = Assistant(llm=llm_cfg,
                system_message=system_instruction)

messages = [{'role': 'user', 'content': "hello"}]
responses = ''
for responses in bot.run(messages=messages):
    pass
print(responses)
