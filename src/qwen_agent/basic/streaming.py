from qwen_agent.agents import Assistant

# Step 2: Configure the LLM you are using.
llm_cfg = {
    # Use the model service provided by DashScope:
    'model': 'qwen2.5:3b',
    'model_server': 'http://localhost:11434/v1',
    'api_key': 'EMPTY',
    # 'api_key': 'YOUR_DASHSCOPE_API_KEY',
    # It will use the `DASHSCOPE_API_KEY' environment variable if 'api_key' is not set here.

    # Use a model service compatible with the OpenAI API, such as vLLM or Ollama:
    # 'model': 'Qwen2.5-7B-Instruct',
    # 'model_server': 'http://localhost:8000/v1',  # base_url, also known as api_base
    # 'api_key': 'EMPTY',

    # (Optional) LLM hyperparameters for generation:
    'generate_cfg': {
        'top_p': 0.8,
        'temperature': 0.7,
        'max_tokens': 2048,
    }
}

# Step 3: Create an agent. Here we use the `Assistant` agent as an example, which is capable of using tools and reading files.
system_instruction = '''You are a helpful assistant.'''
bot = Assistant(llm=llm_cfg,
                system_message=system_instruction)

# Step 4: Run the agent as a chatbot.
messages = []  # This stores the chat history.
while True:
    # For example, enter the query "draw a dog and rotate it 90 degrees".
    query = input('\nuser query: ')
    # Append the user query to the chat history.
    messages.append({'role': 'user', 'content': query})

    response = ''
    for chunk in bot.run(messages):
        current_message = chunk[0]['content']
        if current_message:
            print(current_message, end="\r", flush=True)  # Works only in debug mode
            response = current_message
        else:
            print("no content", flush=True)

    print('bot response:')
    print(response)
    messages.append({'role': 'assistant', 'content': response})
