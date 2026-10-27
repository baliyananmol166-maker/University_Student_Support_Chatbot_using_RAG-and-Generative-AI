# University Student Support Chatbot Using RAG and Generative AI

An AI-powered student support chatbot that helps students find university-related information using Retrieval-Augmented Generation (RAG), semantic search, and Google Gemini.

## About the Project

The chatbot retrieves relevant information from a university student-support knowledge base and uses a generative AI model to produce helpful answers.

The project is designed around ABES Engineering College student support, including academic calendars, examinations, attendance, ERP guidance, scholarships, and college resources.

## Features

- AI-powered question answering with Google Gemini
- Retrieval-Augmented Generation (RAG)
- Semantic search using FAISS
- Sentence Transformer embeddings
- Flask backend with a web-based interface
- CSV-based student support knowledge base
- Retrieved source categories and source information

## Technology Stack

| Component | Technology |
|---|---|
| Programming language | Python |
| Backend | Flask |
| Generative AI | Google Gemini |
| RAG framework | LangChain |
| Vector database | FAISS |
| Embeddings | Sentence Transformers |
| Frontend | HTML, CSS, JavaScript |
| Dataset | CSV |

## Project Structure

```text
AI_Chatbot/
├── backend/
│   ├── app.py
│   ├── create_vectorstore.py
│   ├── rag.py
│   └── test_rag.py
├── data/
│   └── University_Student_Support_RAG_Dataset.csv
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── style.css
├── .gitignore
├── requirements.txt
└── README.md
```

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/baliyananmol166-maker/University_Student_Support_Chatbot_using_RAG-and-Generative-AI.git
cd University_Student_Support_Chatbot_using_RAG-and-Generative-AI
```

### 2. Create and activate a virtual environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure your Gemini API key

Create a `.env` file in the project root with the following line:

```text
GOOGLE_API_KEY=your_actual_gemini_api_key
```

Replace the placeholder with your own API key. Never upload your `.env` file or expose your API key publicly.

### 5. Build the vector database

The vector database is generated locally from the CSV dataset.

```powershell
python .\backend\create_vectorstore.py
```

This downloads and loads the embedding model if necessary, creates the FAISS index, and saves it in the `vectorstore` directory.

### 6. Run the chatbot

```powershell
python .\backend\app.py
```

Open this URL in your browser:

http://127.0.0.1:5000

## Official College Resources

- [ABES Engineering College](https://www.abes.ac.in/)
- [Academic Calendar](https://www.abes.ac.in/Academic-Calender.html)
- [College Circulars and Notices](https://www.abes.ac.in/circulars.html)

## Future Enhancements

- Improve retrieval accuracy and evaluation
- Expand the verified university knowledge base
- Improve the user interface and mobile responsiveness
- Add automated testing
- Deploy the chatbot online

## Disclaimer

This chatbot is an academic project intended to assist students in finding information. Academic dates and institutional policies may change. Always verify important information using official college notices and resources.