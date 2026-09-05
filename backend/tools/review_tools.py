from langchain_core.tools import tool

from chains.review_chain import create_resume_review_chain
from services.resume_service import get_resume_text


@tool
def analyze_resume_for_job(job_description: str) -> dict:
    """
    Analyze the uploaded resume against a job description.

    Use this tool when the user wants ATS scoring, skill gap analysis,
    keyword comparison, strengths, weaknesses, or suggestions for
    improving the resume for a specific job.
    """
    if isinstance(job_description, dict):
        job_description = job_description.get("job_description") or job_description.get("query") or str(job_description)
    elif not isinstance(job_description, str):
        job_description = str(job_description)

    print(f"[TOOL CALL] Executing: analyze_resume_for_job")
    print(f"[ARGUMENT]  JD Snippet: '{job_description[:90]}...'")

    resume_text = get_resume_text()

    review_chain = create_resume_review_chain()

    result = review_chain.invoke(
        {
            "resume": resume_text,
            "job_description": job_description,
        }
    )

    return result.model_dump()