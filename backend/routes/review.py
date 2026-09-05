from fastapi import APIRouter
from pydantic import BaseModel

from chains.review_chain import create_resume_review_chain
from services.resume_service import get_resume_text

router = APIRouter()


class ATSRequest(BaseModel):
    job_description: str

@router.post("/ats")
@router.post("/review")
async def review_resume(request: ATSRequest):
    resume_text = get_resume_text()
    review_chain = create_resume_review_chain()
    review = review_chain.invoke(
        {
            "resume": resume_text,
            "job_description": request.job_description,
        }
    )

    return review.model_dump()
