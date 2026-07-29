from fastapi import APIRouter

from chains.review_chain import create_resume_review_chain
from services.resume_service import get_resume_text

router = APIRouter()

@router.post("/review")
async def review_resume():
    resume_text = get_resume_text()
    review_chain = create_resume_review_chain()
    review = review_chain.invoke({"resume": resume_text})

    return {
    "review": review
    }
