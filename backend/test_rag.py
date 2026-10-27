import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
# Project paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VECTORSTORE_DIR = os.path.join(
    BASE_DIR,
    "vectorstore"
)
# Load embedding model
print("Loading embedding model...")
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
# Load FAISS database
print("Loading FAISS vector database...")
vectorstore = FAISS.load_local(
    VECTORSTORE_DIR,
    embeddings,
    allow_dangerous_deserialization=True
)
# Ask a test question
question = "What is the location of ABES Engineering College?"
print("\nQuestion:")
print(question)
# Search for relevant documents
results = vectorstore.similarity_search(
    question,
    k=3
)
print("\nRetrieved documents:")
print("=" * 60)
for i, doc in enumerate(results, start=1):
    print(f"\nResult {i}")
    print("-" * 60)
    print("Category:", doc.metadata.get("category"))
    print("Source:", doc.metadata.get("source"))
    print("Verified:", doc.metadata.get("verified"))
    print("\nContent:")
    print(doc.page_content)
print("\n" + "=" * 60)
print("RAG SEARCH TEST COMPLETED!")