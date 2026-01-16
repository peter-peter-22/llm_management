from qwen_agent.agents import Assistant

from src.qwen_agent.ui.gui.web_ui import WebUI

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

if __name__ == '__main__':
    system_instruction = '''You are a helpful assistant.'''
    bot = Assistant(llm=llm_cfg, system_message=system_instruction, name="test", description="test assistant")
    chatbot_config = {
        'prompt.suggestions': [
            "hello"
        ],
        'input.placeholder': "Ask something"
    }
    WebUI(bot, chatbot_config).run(server_port=8080, share=False)
