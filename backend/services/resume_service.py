from pathlib import Path
import re

from fastapi import HTTPException
from langchain_community.document_loaders import PyPDFLoader

from config import UPLOAD_DIR


def clean_text(text: str) -> str:

    text = re.sub(r"\s+", " ", text)
    return text.strip()


def load_resume_documents():

    resume_path = Path(UPLOAD_DIR) / "resume.pdf"

    if not resume_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Resume not found. Please upload a resume first.",
        )

    loader = PyPDFLoader(str(resume_path))
    documents = loader.load()

    if not documents:
        raise HTTPException(
            status_code=400,
            detail="The uploaded resume is empty or could not be read.",
        )

    for doc in documents:
        doc.page_content = clean_text(doc.page_content)

    return documents


def get_resume_text():

    documents = load_resume_documents()

    resume_text = "\n\n".join(
        doc.page_content for doc in documents
    )

    if not resume_text.strip():
        raise HTTPException(
            status_code=400,
            detail="The uploaded resume contains no readable text.",
        )

    return resume_text