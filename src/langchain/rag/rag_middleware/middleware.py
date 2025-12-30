from langchain.agents.middleware import dynamic_prompt, ModelRequest

from src.langchain.rag.vector_search import vector_store


@dynamic_prompt
def prompt_with_context(request: ModelRequest) -> str:
    """Inject context into state messages."""
    last_query = request.state["messages"][-1].text
    retrieved_docs = vector_store.similarity_search(last_query, 3)

    docs_content = "\n\n".join(doc.page_content for doc in retrieved_docs)

    system_message = (
        "The following context is possibly relevant to you:\n."
        f"\n\n{docs_content}"
    )

    print("RAG:", system_message)

    return system_message
