from pathlib import Path
import shutil

from fastapi import APIRouter, File, UploadFile
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel

from chains import create_rag_chain
from config import CHUNK_OVERLAP, CHUNK_SIZE, UPLOAD_DIR
from services.resume_service import load_resume_documents
from vectorstore import create_vector_store, get_retriever


router = APIRouter()


class QuestionRequest(BaseModel):
    question: str


@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    file_path = Path(UPLOAD_DIR) / "resume.pdf"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    documents = load_resume_documents()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )

    chunks = text_splitter.split_documents(documents)

    create_vector_store(chunks)

    return {
        "filename": file.filename,
        "file_path": str(file_path),
        "num_pages": len(documents),
        "num_chunks": len(chunks),
    }


@router.post("/ask")
async def ask_resume(request: QuestionRequest):
    retriever = get_retriever()

    rag_chain = create_rag_chain(retriever)

    answer = rag_chain.invoke(request.question)

    return {
        "question": request.question,
        "answer": answer,
    }