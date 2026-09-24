# 🧠 DocuMind AI — Intelligent PDF Analyzer

An AI-powered PDF question-answering app. Upload any PDF and ask natural language questions — the app retrieves the most relevant sections and generates precise, context-aware answers using Google Gemini, with page-level source citations.

## ✨ Features

- 📄 Upload and parse any PDF document
- 🔍 Semantic search over document content using vector embeddings
- 💬 Ask natural language questions and get context-grounded answers
- 📚 Source citations with page numbers and excerpts for every answer
- 🧵 Persistent conversation history within a session
- 🎨 Clean, modern dark-themed UI

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| Backend | FastAPI |
| LLM | Google Gemini (`gemini-3.1-flash-lite`) |
| Orchestration | LangChain |
| Embeddings | HuggingFace `all-MiniLM-L6-v2` (local, free) |
| Vector Store | ChromaDB |
| PDF Parsing | PyPDF |

## 📂 Project Structure

```
MY_Rag_Project/
├── backend/
│   ├── main.py            # FastAPI server: /upload and /ask endpoints
│   ├── requirements.txt   # Python dependencies
│   └── .env                # API keys (not committed)
├── frontend/
│   └── app.py              # Streamlit UI
└── README.md
```

## ⚙️ Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
cd YOUR-REPO-NAME
```

### 2. Backend setup
```bash
cd backend
pip install -r requirements.txt
```

Create a `.env` file inside `backend/` with your Gemini API key:
```
GOOGLE_API_KEY=your_google_api_key_here
```
> Get a free API key from [Google AI Studio](https://aistudio.google.com/apikey).

### 3. Run the backend
```bash
python -m uvicorn main:app --reload
```
Backend runs at `http://127.0.0.1:8000`

### 4. Frontend setup (in a new terminal)
```bash
cd frontend
pip install streamlit requests
streamlit run app.py
```
Frontend opens automatically at `http://localhost:8501`

## 🚀 Usage

1. Upload a PDF from the sidebar and click **Process Document**
2. Wait for indexing to complete
3. Type a question in the input box and hit **Ask →**
4. View the answer along with source page references and excerpts

## 📌 Notes

- Uses Gemini's free tier — request limits apply (see [Gemini rate limits](https://ai.google.dev/gemini-api/docs/rate-limits))
- Embeddings run locally via HuggingFace, so no extra API cost for indexing
- `.env`, `__pycache__/`, and local vector store data are excluded from version control

## 📄 License

This project is for educational purposes.
