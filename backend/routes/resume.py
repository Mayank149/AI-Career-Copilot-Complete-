from pathlib import Path
import shutil

from fastapi import APIRouter, File, UploadFile
from pydantic import BaseModel

from chains.rag import create_rag_chain
from config import UPLOAD_DIR
from services.resume_service import load_resume_documents
from vectorstore import get_retriever, reindex_active_resume


router = APIRouter()


class QuestionRequest(BaseModel):
    question: str


@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    file_path = Path(UPLOAD_DIR) / "resume.pdf"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    num_chunks = reindex_active_resume()
    documents = load_resume_documents()

    return {
        "filename": file.filename,
        "file_path": str(file_path),
        "num_pages": len(documents),
        "num_chunks": num_chunks,
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