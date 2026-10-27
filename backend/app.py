import os
from flask import (
    Flask,
    request,
    jsonify,
    render_template
)
from rag import ask_question
# =========================================================
# PROJECT PATHS
# =========================================================
BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)
FRONTEND_DIR = os.path.join(
    BASE_DIR,
    "frontend"
)
# =========================================================
# FLASK APP
# =========================================================
app = Flask(
    __name__,
    template_folder=FRONTEND_DIR,
    static_folder=FRONTEND_DIR,
    static_url_path="/static"
)
# =========================================================
# HOME PAGE
# =========================================================
@app.route("/")
def home():

    return render_template(
        "index.html"
    )
# =========================================================
# CHAT API
# =========================================================
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json(
            silent=True
        ) or {}
        question = data.get(
            "question",
            ""
        ).strip()
        if not question:
            return jsonify({
                "error": "Please enter a question."
            }), 400
        # Ask RAG chatbot
        answer, documents = ask_question(
            question
        )
        # Prepare sources
        sources = []
        for document in documents:
            metadata = document.metadata
            sources.append({
                "category": metadata.get(
                    "category",
                    "Unknown"
                ),
                "source": metadata.get(
                    "source",
                    "University Student Support Dataset"
                ),
                "verified": metadata.get(
                    "verified",
                    False
                )
            })
        return jsonify({
            "answer": answer,
            "sources": sources
        })
    except Exception as error:
        app.logger.exception(
            "Chatbot request failed"
        )
        return jsonify({
            "error":
            "Something went wrong. "
            "Please try again."
        }), 500
# =========================================================
# RUN SERVER
# =========================================================
if __name__ == "__main__":
    print("\n==========================================")
    print("UNIVERSITY STUDENT SUPPORT CHATBOT")
    print("==========================================")
    print(
        "Open http://127.0.0.1:5000 "
        "in your browser."
    )
    print("==========================================\n")
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )