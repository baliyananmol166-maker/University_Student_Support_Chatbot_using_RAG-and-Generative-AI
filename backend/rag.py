
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
    os.path.dirname(os.path.abspath(__file__))
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
# LOAD FAISS VECTOR STORE
# =========================================================

print("Loading student support knowledge base...")

if not os.path.isdir(VECTORSTORE_DIR):
    raise FileNotFoundError(
        f"Vector store directory not found: {VECTORSTORE_DIR}. "
        "Run backend/create_vectorstore.py first."
    )

vectorstore = FAISS.load_local(
    VECTORSTORE_DIR,
    embeddings,
    allow_dangerous_deserialization=True
)


# =========================================================
# GEMINI CONFIGURATION
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
You are the University Student Support Chatbot for ABES
Engineering College, when the retrieved knowledge confirms
that the question concerns ABES. Help students with clear,
accurate and practical answers.

FOLLOW THESE RULES CAREFULLY:

1. ACCURACY
- Use the retrieved knowledge as the primary source for
  ABES-specific facts.
- Never invent college policies, dates, fees, deadlines,
  percentages, course names, contacts or procedures.
- Do not assume that information is current simply because
  it appears in the knowledge base.
- If retrieved information conflicts, explain the conflict
  and recommend checking the latest official notice.

2. COLLEGE TERMINOLOGY
- Refer to ABES Engineering College as a college, not as
  a university.
- Do not call another institution ABES or attribute its
  information to ABES.
- Use the institution's name only when supported by context.

3. OFFICIAL SOURCES AND GENERAL GUIDANCE
- Examine the category, source, verification metadata and
  content supplied in the retrieved knowledge.
- Call information officially verified only when the
  retrieved source or metadata supports that description.
- Do not assume an entry is official merely because it is
  present in the dataset.
- Clearly distinguish general advice from verified
  college-specific rules.
- If exact information is missing, provide useful general
  guidance when appropriate and explain how to verify the
  college-specific answer.
- Never invent an official contact, link or policy.

4. COURSE AND PROGRAMME QUESTIONS
- List only courses or programmes supported by the retrieved
  information.
- Do not claim a list is complete unless the retrieved
  information explicitly establishes that it is complete.
- If completeness is uncertain, say that the list may not
  be exhaustive and recommend checking the official courses
  page: https://www.abes.ac.in/courses-offered.html
- Do not invent admission eligibility, intake or fees.

5. ACADEMIC CALENDAR AND EXAMINATIONS
- Preserve exact dates and percentages only when supported
  by relevant retrieved information.
- If a calendar is described as tentative or subject to
  revision, clearly preserve that qualification.
- Do not treat a previous calendar as proof of a current
  schedule.
- Recommend checking the latest official calendar or
  circular when dates or rules may have changed.
- Do not generalize one programme's dates or rules to every
  programme without evidence.

6. PROCEDURAL QUESTIONS
- Explain steps in a numbered list when helpful.
- For ERP, password resets, scholarships and other processes,
  give exact steps only when supported by the context.
- If a procedure cannot be verified, describe it as general
  guidance rather than a confirmed ABES procedure.
- Include links only when supplied by the retrieved
  knowledge or when they are explicitly listed in these
  instructions as an official verification page.
- Never ask students to share passwords, OTPs or other
  secret credentials.

7. MISSING INFORMATION
- Do not fabricate an answer to fill a gap.
- If the context does not establish the answer, state what
  could not be verified and suggest a relevant official
  source or college support channel.
- Do not say that no information exists when the context
  contains a useful partial answer.

8. RESPONSE STYLE
- Be concise, friendly, respectful and student-friendly.
- Use readable paragraphs, numbered steps or bullet points.
- Avoid repeating the same warning unnecessarily.
- Answer the student's actual question directly.

RETRIEVED KNOWLEDGE:
{context}

STUDENT QUESTION:
{question}

Write the best accurate answer supported by the retrieved
knowledge and the rules above.
"""


# =========================================================
# METADATA HELPERS
# =========================================================

def get_metadata_value(metadata, *keys, default="Not provided"):
    """Return the first available non-empty metadata value."""

    for key in keys:
        value = metadata.get(key)

        if value is not None and str(value).strip():
            return str(value).strip()

    return default


# =========================================================
# BUILD RETRIEVED CONTEXT
# =========================================================

def build_context(documents_with_scores):
    """Build context with relevant source and verification metadata."""

    context_parts = []

    for number, (document, score) in enumerate(
        documents_with_scores,
        start=1
    ):
        metadata = document.metadata or {}

        category = get_metadata_value(
            metadata,
            "category"
        )

        source = get_metadata_value(
            metadata,
            "source",
            "source_name",
            "url"
        )

        verified = get_metadata_value(
            metadata,
            "verified",
            "Verified",
            "is_verified"
        )

        original_question = get_metadata_value(
            metadata,
            "question",
            default=""
        )

        entry = (
            f"RECORD {number}\n"
            f"CATEGORY: {category}\n"
            f"SOURCE: {source}\n"
            f"VERIFICATION METADATA: {verified}\n"
            f"RELATED QUESTION: {original_question}\n"
            f"CONTENT:\n{document.page_content}"
        )

        context_parts.append(entry)

    return "\n\n====================\n\n".join(context_parts)


# =========================================================
# ASK QUESTION
# =========================================================

def ask_question(question):

    question = question.strip()

    if not question:
        return "Please enter a question.", []

    # -----------------------------------------------------
    # RETRIEVE RELEVANT DOCUMENTS
    # -----------------------------------------------------

    try:
        documents_with_scores = (
            vectorstore.similarity_search_with_score(
                question,
                k=6
            )
        )

    except Exception as exc:
        print(f"Retrieval error: {exc}")

        return (
            "I'm unable to search the student support "
            "knowledge base right now. Please try again later."
        ), []

    documents = [
        document
        for document, score in documents_with_scores
    ]

    # -----------------------------------------------------
    # RETRIEVAL DEBUG INFORMATION
    # -----------------------------------------------------

    print("\n" + "-" * 50)
    print("RETRIEVAL DEBUG")
    print("-" * 50)

    print("Question:", question)
    print("Retrieved documents:", len(documents_with_scores))

    for number, (document, score) in enumerate(
        documents_with_scores,
        start=1
    ):
        metadata = document.metadata or {}

        print(f"\n{number}.")
        print(
            "Category:",
            metadata.get("category", "Unknown")
        )
        print(
            "Source:",
            metadata.get("source", "Not provided")
        )
        print(
            "Verified:",
            metadata.get(
                "verified",
                metadata.get("Verified", "Not provided")
            )
        )
        print(f"Distance: {score:.4f}")
        print(
            "Related question:",
            metadata.get("question", "")
        )

    print("-" * 50 + "\n")

    # -----------------------------------------------------
    # HANDLE EMPTY RETRIEVAL
    # -----------------------------------------------------

    if not documents_with_scores:
        return (
            "I couldn't find relevant information in the "
            "current student support knowledge base. "
            "Please check the official ABES website or the "
            "latest college notice for accurate information."
        ), []

    # -----------------------------------------------------
    # BUILD CONTEXT AND PROMPT
    # -----------------------------------------------------

    context = build_context(documents_with_scores)

    prompt = SYSTEM_PROMPT.format(
        context=context,
        question=question
    )

    # -----------------------------------------------------
    # GENERATE ANSWER
    # -----------------------------------------------------

    try:
        response = llm.invoke(prompt)

    except Exception as exc:
        print(f"Gemini response error: {exc}")

        return (
            "I'm unable to generate an answer right now. "
            "Please try again in a moment."
        ), documents

    # -----------------------------------------------------
    # EXTRACT RESPONSE TEXT
    # -----------------------------------------------------

    answer = response.content

    if isinstance(answer, list):
        text_parts = []

        for item in answer:
            if isinstance(item, str):
                text_parts.append(item)

            elif isinstance(item, dict):
                if isinstance(item.get("text"), str):
                    text_parts.append(item["text"])

        answer = "\n".join(text_parts)

    elif not isinstance(answer, str):
        answer = str(answer)

    answer = answer.strip()

    if not answer:
        answer = (
            "I couldn't generate a useful answer. "
            "Please rephrase your question or try again."
        )

    return answer, documents


# =========================================================
# TERMINAL TEST
# =========================================================

if __name__ == "__main__":

    print("\n" + "=" * 50)
    print("UNIVERSITY STUDENT SUPPORT CHATBOT")
    print("=" * 50)
    print("Type 'exit' to stop.\n")

    while True:

        question = input("Student: ").strip()

        if question.lower() in ["exit", "quit", "stop"]:
            print("Chatbot: Goodbye!")
            break

        answer, documents = ask_question(question)

        print("\nChatbot:")
        print(answer)

        print("\nRetrieved source categories:")

        for document in documents:
            metadata = document.metadata or {}

            print(
                "-",
                metadata.get("category", "Unknown")
            )

        print("\n" + "=" * 50 + "\n")
