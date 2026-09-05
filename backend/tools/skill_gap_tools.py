from langchain_core.tools import tool
from services.resume_service import get_resume_text
from services.llm_service import get_llm

@tool
def analyze_skill_gap(target_role : str) -> str:
    """
    Analyze the candidate's uploaded resume and identify skill gaps
    for a target job role.

    Use this when the user asks what skills they are missing,
    what they should learn, or how their current profile compares
    to a specific target role.
    """

    if isinstance(target_role, dict):
        target_role = target_role.get("target_role") or target_role.get("query") or str(target_role)
    elif not isinstance(target_role, str):
        target_role = str(target_role)

    print(f"[TOOL CALL] Executing: analyze_skill_gap")
    print(f"[ARGUMENT]  Target Role: '{target_role}'")


    resume_text = get_resume_text()
    llm = get_llm()

    prompt = f"""
You are an AI career advisor.

Analyze the candidate's resume and identify their skill gaps
for the target role.

Target Role:
{target_role}

Resume:
{resume_text}

Provide:

1. Current relevant skills
2. Missing or weak skills
3. Skills that should be prioritized
4. Practical steps to address skill gaps

Formatting Instructions:
- Do not use markdown header hashtags (do not use #, ##, or ###).
- Use clean bold titles (e.g. **Current Relevant Skills**), bullet points, and numbered lists.
- Keep responses well-organized, clean, and direct.

Only use information from the resume when describing the
candidate's current skills and experience.

Do not claim the candidate knows a skill unless it appears
in the resume.
"""

    response = llm.invoke(prompt)
    return response.content