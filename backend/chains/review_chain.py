from typing import List

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from services.llm_service import get_llm


class ATSAnalysis(BaseModel):
    overall_score: int = Field(..., ge=0, le=100)
    keyword_match: int = Field(..., ge=0, le=100)
    missing_keywords: List[str]
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[str]


parser = PydanticOutputParser(pydantic_object=ATSAnalysis)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are an ATS scoring assistant for technical recruiting.

Compare the candidate's resume against the job description.

Evaluate:
- Overall ATS fit
- Keyword coverage
- Missing keywords that matter for the role
- Resume strengths relative to the job description
- Resume weaknesses relative to the job description
- Concrete suggestions to improve ATS alignment

Only use the information present in the resume and job description.
Do not invent experience, projects, or skills.

Be constructive and specific.

If information is missing, explicitly mention it instead of making assumptions.

Return a single JSON object with exactly these keys:

- overall_score
- keyword_match
- missing_keywords
- strengths
- weaknesses
- suggestions

The JSON must contain integers for overall_score and keyword_match in the range 0 to 100.
The JSON must not include markdown, code fences, or any extra text.

{format_instructions}
"""
        ),
        (
            "human",
            """
Resume:

{resume}

Job Description:

{job_description}
"""
        ),
    ]
)

def create_resume_review_chain():
    llm = get_llm()
    return (
        prompt
        .partial(format_instructions=parser.get_format_instructions())
        | llm
        | parser
    )