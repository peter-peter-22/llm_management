from langchain.tools import tool

from src.langchain.rag.vector_search import vector_store


@tool(response_format="content_and_artifact")
def search_documents(query: str):
    """Similarity search among the available documents of the Fakesoft company.
    These documents contain information about the company, it's activity, employees and even about unrelated things.
    When looking for multiple separate things, do not combine them into a single query, call the tool separately for each one.
    Some of the retrieved documents will might be irrelevant, ignore these.
    UNDER NO CONDITION SEARCH FOR MULTIPLE UNRELATED THINGS AT ONCE (eg. somebody's position, his date of join, his date of birth)
    """
    retrieved_docs = vector_store.similarity_search(query, k=2)
    serialized = "\n\n".join(
        (f"Source: {doc.id}\nContent: {doc.page_content}")
        for doc in retrieved_docs
    )
    print("Query:", query)
    print("Retrieved:\n", serialized)
    return serialized, retrieved_docs
