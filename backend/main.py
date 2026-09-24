import os
import shutil
import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

app = FastAPI(title="PDF Analyzer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

session_data = {
    "vectorstore": None,
    "file_name": None,
    "total_pages": 0,
    "total_chunks": 0
}

# Local open-source embeddings (Free, Fast, no API calls)
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# LLM initialised once at startup — reused across all /ask requests
def get_llm():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GOOGLE_API_KEY is missing.")
    return ChatGoogleGenerativeAI(
        model="gemini-3.1-flash-lite",
        google_api_key=api_key,
    )

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

class QueryRequest(BaseModel):
    question: str

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GOOGLE_API_KEY is not set in .env file.")
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        loader = PyPDFLoader(tmp_path)
        raw_docs = loader.load()

        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
        chunks = splitter.split_documents(raw_docs)

        vectorstore = Chroma.from_documents(documents=chunks, embedding=embeddings)

        session_data["vectorstore"] = vectorstore
        session_data["file_name"] = file.filename
        session_data["total_pages"] = len(raw_docs)
        session_data["total_chunks"] = len(chunks)

        return {
            "status": "success",
            "fileName": file.filename,
            "totalPages": len(raw_docs),
            "totalChunks": len(chunks)
        }
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

@app.post("/ask")
async def ask_question(payload: QueryRequest):
    if not session_data["vectorstore"]:
        raise HTTPException(status_code=400, detail="Please upload and process a PDF first.")

    retriever = session_data["vectorstore"].as_retriever(search_kwargs={"k": 4})
    llm = get_llm()

    prompt = ChatPromptTemplate.from_template("""You are an intelligent PDF analyst. Answer the user question using ONLY the provided context.
Format your answer clearly with bullet points where appropriate.
If the answer is not present in the context, strictly state: "I could not find the answer in the uploaded PDF."

Context:
{context}

Question:
{question}
""")

    matching_docs = retriever.invoke(payload.question)
    context_text = format_docs(matching_docs)

    chain = prompt | llm | StrOutputParser()

    try:
        answer = chain.invoke({"context": context_text, "question": payload.question})
    except Exception as e:
        err_msg = str(e)
        if "RESOURCE_EXHAUSTED" in err_msg or "429" in err_msg:
            raise HTTPException(
                status_code=429,
                detail="Gemini API rate limit hit. Please wait a bit and try again."
            )
        raise HTTPException(status_code=500, detail=f"LLM error: {err_msg}")

    sources = [
        {
            "page": doc.metadata.get("page", 0) + 1,
            "content": (doc.page_content[:300] + "…") if len(doc.page_content) > 300 else doc.page_content,
        }
        for doc in matching_docs
    ]

    return {
        "answer": answer,
        "sources": sources
    }