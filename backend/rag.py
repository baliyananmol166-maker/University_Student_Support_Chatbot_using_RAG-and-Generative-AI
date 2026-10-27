import os

from dotenv import load_dotenv

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI


# =========================================================
# LOAD ENVIRONMENT
# =========================================================

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError(
        "GOOGLE_API_KEY is missing. Please check your .env file."
    )


# =========================================================
# PROJECT PATH
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

VECTORSTORE_DIR = os.path.join(
    BASE_DIR,
    "vectorstore"
)


# =========================================================
# EMBEDDINGS
# =========================================================

print("Loading embedding model...")

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


# =========================================================
# LOAD FAISS
# =========================================================

print("Loading university knowledge base...")

vectorstore = FAISS.load_local(
    VECTORSTORE_DIR,
    embeddings,
    allow_dangerous_deserialization=True
)


# =========================================================
# GEMINI
# =========================================================

print("Connecting to Gemini...")

llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    google_api_key=GOOGLE_API_KEY,
    max_retries=3
)


# =========================================================
# SYSTEM PROMPT
# =========================================================

SYSTEM_PROMPT = """
You are a University Student Support Chatbot.

You help students with university-related questions.

IMPORTANT:

1. Answer the student's question using the retrieved knowledge.
2. Prefer the most relevant retrieved information.
3. Do not invent university-specific facts.
4. Do not invent exact dates, fees, deadlines, percentages,
   policies, contact numbers, or course names.
5. If the retrieved knowledge contains a general procedure,
   explain that procedure clearly.
6. If exact university-specific information is unavailable,
   explain the general procedure and tell the student where
   to verify the exact information.
7. Do NOT say "information is not available" if the retrieved
   knowledge contains a useful general answer.
8. Keep the answer clear and student-friendly.
9. Do not mention ABES or any specific university unless it
   appears in the retrieved knowledge.

RETRIEVED KNOWLEDGE:

{context}

STUDENT QUESTION:

{question}

Write a helpful answer now.
"""


# =========================================================
# ASK QUESTION
# =========================================================

def ask_question(question):

    question = question.strip()

    if not question:
        return "Please enter a question.", []


    # =====================================================
    # RETRIEVE RELEVANT DOCUMENTS
    # =====================================================

    documents_with_scores = (
        vectorstore.similarity_search_with_score(
            question,
            k=6
        )
    )


    documents = [
        document
        for document, score
        in documents_with_scores
    ]


    # =====================================================
    # SHOW RETRIEVAL INFORMATION
    # =====================================================

    print("\n------------------------------------------")
    print("RETRIEVAL DEBUG")
    print("------------------------------------------")

    print("Question:")
    print(question)

    print("\nRetrieved documents:")

    for number, (document, score) in enumerate(
        documents_with_scores,
        start=1
    ):

        print(
            f"\n{number}. "
            f"Category: "
            f"{document.metadata.get('category', 'Unknown')}"
        )

        print(
            f"Distance: {score:.4f}"
        )

        print(
            "Question:",
            document.metadata.get(
                "question",
                ""
            )
        )

    print("------------------------------------------\n")


    # =====================================================
    # BUILD CONTEXT
    # =====================================================

    context_parts = []

    for document, score in documents_with_scores:

        context_parts.append(

            "CATEGORY: "
            + str(
                document.metadata.get(
                    "category",
                    ""
                )
            )

            + "\n"

            + document.page_content
        )


    context = "\n\n====================\n\n".join(
        context_parts
    )


    # =====================================================
    # PROMPT
    # =====================================================

    prompt = SYSTEM_PROMPT.format(
        context=context,
        question=question
    )


    # =====================================================
    # GEMINI
    # =====================================================

    response = llm.invoke(
        prompt
    )


    # =====================================================
    # RESPONSE TEXT
    # =====================================================

    answer = response.content


    if isinstance(answer, list):

        text_parts = []

        for item in answer:

            if isinstance(item, dict):

                if "text" in item:

                    text_parts.append(
                        item["text"]
                    )

            elif isinstance(item, str):

                text_parts.append(
                    item
                )

        answer = "\n".join(
            text_parts
        )


    answer = str(
        answer
    ).strip()


    if not answer:

        answer = (
            "I could not generate an answer "
            "from the current university knowledge base."
        )


    return answer, documents


# =========================================================
# TERMINAL TEST
# =========================================================

if __name__ == "__main__":

    print("\n==========================================")
    print("UNIVERSITY STUDENT SUPPORT CHATBOT")
    print("==========================================")
    print("Type 'exit' to stop.\n")


    while True:

        question = input(
            "Student: "
        ).strip()


        if question.lower() in [
            "exit",
            "quit",
            "stop"
        ]:

            print(
                "Chatbot: Goodbye!"
            )

            break


        answer, documents = ask_question(
            question
        )


        print("\nChatbot:")
        print(answer)


        print("\nSources:")

        for document in documents:

            print(
                "-",
                document.metadata.get(
                    "category",
                    "Unknown"
                )
            )


        print(
            "\n" + "=" * 50 + "\n"
        )