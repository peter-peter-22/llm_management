# Import necessary modules from LangChain
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document  # Document class
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter  # For chunking documents

# Step 1: Prepare your documents (same as before)
documents = [
    Document(
        page_content="John Doe is a AI engineer at Fakesoft and he loves cats."),
    Document(
        page_content="John Doe loves cookies and milk."),
    Document(
        page_content="The Eiffel tower is in France"),
    Document(
        page_content="Milk is white."),
    Document(
        page_content="Mister Anderson loves apples but dislikes milk."),
    Document(
        page_content="The position of John Doe is AI engineer."),
    Document(
        page_content="John Doe joined the company in 2022."),
    Document(
        page_content="The alternative name of Fakesoft is Mangosoft."),
]

# Step 2: Split documents into chunks (same)
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,  # Max characters per chunk
    chunk_overlap=100  # Overlap for context
)
chunks = text_splitter.split_documents(documents)

embeddings = OllamaEmbeddings(
    model="mxbai-embed-large:335m")  # Use a dedicated embedding model; assumes Ollama is running
vector_store = FAISS.from_documents(chunks, embeddings)

# print(vector_store.similarity_search("Who is John Doe?", 2))
# print(vector_store.similarity_search("John Doe work location", 2))
