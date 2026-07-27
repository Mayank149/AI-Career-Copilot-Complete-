from fastapi import APIRouter, UploadFile, File
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from vectorstore import create_vector_store, get_retriever
from pydantic import BaseModel
from chains import create_rag_chain
import re

import os
import shutil

class QuestionRequest(BaseModel):
    question: str

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    for doc in documents:
        text = doc.page_content
        # Replace multiple whitespace (spaces, tabs, newlines) with a single space
        text = re.sub(r"\s+", " ", text)
        # Remove leading/trailing whitespace
        text = text.strip()
        doc.page_content = text

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 500,
        chunk_overlap = 100
    )

    chunks = text_splitter.split_documents(documents)
    
    create_vector_store(chunks)
    
    return {
        "filename": file.filename,
        "file_path": file_path,
        "num_pages": len(documents),
        "num_chunks": len(chunks)
    }

@router.post("/ask")
async def ask_resume(request: QuestionRequest):
    retriever = get_retriever()
    
    rag_chain = create_rag_chain(retriever)

    answer = rag_chain.invoke(request.question)

    return {
        "question": request.question,
        "answer": answer
    }