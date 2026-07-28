from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from vectorstore import get_retriever
from chains import format_docs

router = APIRouter()

class ATSRequest(BaseModel):
    job_description: str

@router.post("/analyze")
def analyze_resume(request: ATSRequest):

    return {
        "job_description": request.job_description
    }