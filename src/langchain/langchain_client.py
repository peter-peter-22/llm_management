from langchain_ollama import ChatOllama

llm = ChatOllama(model="llama3.2:3b", temperature=0)
creative_llm = ChatOllama(model="llama3.2:3b",
                          temperature=0.7)  # Less deterministic. Tries a different approach when fails.
simple_llm = ChatOllama(model="llama3.2:1b", temperature=0)  # Faster but can't call tools.
