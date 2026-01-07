from langchain_ollama import ChatOllama

llm = ChatOllama(model="llama3.2:3b", temperature=0.0)
simple_llm = ChatOllama(model="llama3.2:1b", temperature=0)  # Faster but can't call tools.
