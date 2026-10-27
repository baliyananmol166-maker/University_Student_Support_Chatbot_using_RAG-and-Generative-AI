import os
import csv

from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATA_FILE = os.path.join(
    BASE_DIR,
    "data",
    "University_Student_Support_RAG_Dataset.csv"
)

VECTORSTORE_DIR = os.path.join(
    BASE_DIR,
    "vectorstore"
)


# --------------------------------------------------
# CHECK DATASET
# --------------------------------------------------

print("\nLoading university student support dataset...")
print(f"Dataset: {DATA_FILE}")


if not os.path.exists(DATA_FILE):
    raise FileNotFoundError(
        f"\nDataset not found:\n{DATA_FILE}\n\n"
        "Please make sure the CSV is inside the data folder."
    )


# --------------------------------------------------
# LOAD CSV
# --------------------------------------------------

documents = []

with open(
    DATA_FILE,
    "r",
    encoding="utf-8-sig",
    newline=""
) as file:

    reader = csv.DictReader(file)

    for row in reader:

        question = str(
            row.get("question", "")
        ).strip()

        answer = str(
            row.get("answer", "")
        ).strip()

        category = str(
            row.get("category", "")
        ).strip()

        document_text = str(
            row.get("document_text", "")
        ).strip()


        # If document_text is missing,
        # create it from question + answer.
        if not document_text:

            document_text = (
                f"Category: {category}\n"
                f"Question: {question}\n"
                f"Answer: {answer}"
            )


        metadata = {
            "document_id": str(
                row.get("document_id", "")
            ),

            "category": category,

            "source": str(
                row.get("source", "")
            ),

            "source_type": str(
                row.get("source_type", "")
            ),

            "document_type": str(
                row.get("document_type", "")
            ),

            "language": str(
                row.get("language", "")
            ),

            "verified": str(
                row.get("verified", "False")
            ),

            "source_url": str(
                row.get("source_url", "")
            )
        }


        documents.append(
            Document(
                page_content=document_text,
                metadata=metadata
            )
        )


# --------------------------------------------------
# DATASET INFORMATION
# --------------------------------------------------

print(
    f"Dataset loaded successfully."
)

print(
    f"Number of records: {len(documents)}"
)


if len(documents) == 0:

    raise ValueError(
        "The dataset contains no records."
    )


# --------------------------------------------------
# SHOW CATEGORIES
# --------------------------------------------------

categories = sorted(
    set(
        document.metadata.get(
            "category",
            ""
        )
        for document in documents
    )
)

print("\nCategories found:")

for category in categories:

    print(
        f"  - {category}"
    )


# --------------------------------------------------
# CREATE EMBEDDINGS
# --------------------------------------------------

print(
    "\nLoading embedding model..."
)

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


# --------------------------------------------------
# CREATE FAISS DATABASE
# --------------------------------------------------

print(
    "\nCreating FAISS vector database..."
)

vectorstore = FAISS.from_documents(
    documents,
    embeddings
)


# --------------------------------------------------
# SAVE VECTOR DATABASE
# --------------------------------------------------

vectorstore.save_local(
    VECTORSTORE_DIR
)


# --------------------------------------------------
# SUCCESS
# --------------------------------------------------

print(
    "\n=========================================="
)

print(
    "VECTOR DATABASE CREATED SUCCESSFULLY"
)

print(
    "=========================================="
)

print(
    f"Records: {len(documents)}"
)

print(
    f"Vector database: {VECTORSTORE_DIR}"
)

print(
    "==========================================\n"
)