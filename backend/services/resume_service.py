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


def get_resume_text() -> str:
    """
    Extracts text from the active resume.pdf preserving line breaks, sections,
    and structure so downstream editing and PDF generation retain proper layout.
    """
    resume_path = Path(UPLOAD_DIR) / "resume.pdf"
    if not resume_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Resume not found. Please upload a resume first.",
        )

    # First attempt: PyMuPDF preserves layout blocks and lines cleanly
    try:
        import pymupdf
        doc = pymupdf.open(str(resume_path))
        full_text = "\n".join(page.get_text() for page in doc)
        if full_text.strip():
            return full_text.strip()
    except Exception as e:
        print(f"[WARN] PyMuPDF extraction failed, falling back to PyPDFLoader: {e}")

    # Fallback: PyPDFLoader
    documents = load_resume_documents()
    resume_text = "\n\n".join(doc.page_content for doc in documents)
    if not resume_text.strip():
        raise HTTPException(
            status_code=400,
            detail="The uploaded resume contains no readable text.",
        )

    return resume_text


def backup_original_resume() -> bool:
    """
    Backs up resume.pdf as resume_original.pdf if a backup doesn't already exist.
    """
    resume_path = Path(UPLOAD_DIR) / "resume.pdf"
    backup_path = Path(UPLOAD_DIR) / "resume_original.pdf"

    if resume_path.exists() and not backup_path.exists():
        import shutil
        shutil.copyfile(resume_path, backup_path)
        return True
    return False


def restore_original_resume() -> bool:
    """
    Restores resume_original.pdf back to resume.pdf and removes the backup.
    """
    resume_path = Path(UPLOAD_DIR) / "resume.pdf"
    backup_path = Path(UPLOAD_DIR) / "resume_original.pdf"

    if not backup_path.exists():
        raise HTTPException(
            status_code=400,
            detail="No original resume backup found to revert to."
        )

    import shutil
    shutil.copyfile(backup_path, resume_path)
    backup_path.unlink()
    return True


def has_original_backup() -> bool:
    """
    Checks if a backup of the original resume exists.
    """
    backup_path = Path(UPLOAD_DIR) / "resume_original.pdf"
    return backup_path.exists()