from typing import TypedDict, NotRequired
from services.resume_service import get_resume_text
from services.llm_service import get_llm, clean_llm_output
from langgraph.graph import StateGraph, START, END
from tools.skill_gap_tools import analyze_skill_gap

class RoadmapState(TypedDict):
    target_role: str
    resume_text: NotRequired[str]
    profile_analysis: NotRequired[str]
    skill_gaps: NotRequired[str]
    priorities: NotRequired[str]
    roadmap: NotRequired[str]

llm = get_llm()

def analyze_profile(state: RoadmapState):
    resume_text = get_resume_text()

    prompt = f"""
You are analyzing a candidate's profile to help create
a career learning roadmap.

The candidate's target role is:

{state["target_role"]}

Resume:

{resume_text}

Identify:

- Current technical skills
- Relevant projects
- Relevant experience
- Existing strengths
- Current level of preparation for the target role

Only use information present in the resume.
Do not invent skills or experience.

Return a clear structured analysis.
Keep the analysis concise.
Use at most 300 words.
Focus only on information useful for creating the roadmap.
Do not output internal monologue or <think> tags.
"""

    response = llm.invoke(prompt)

    return {
        "resume_text": resume_text,
        "profile_analysis": clean_llm_output(response.content)
    }

def analyze_gaps(state: RoadmapState):
    result = analyze_skill_gap.invoke(
        {
            "target_role": state["target_role"]
        }
    )

    return {
        "skill_gaps": clean_llm_output(result)
    }


def prioritize_skills(state: RoadmapState):
    prompt = f"""
You are helping prioritize a candidate's learning path.

Target role:
{state["target_role"]}

Candidate profile:
{state["profile_analysis"]}

Skill gap analysis:
{state["skill_gaps"]}

Prioritize the skills the candidate should focus on.

For each priority, explain:
- What to learn
- Why it matters for the target role
- Why it should be learned before or after other skills

Group the priorities into:

1. High priority
2. Medium priority
3. Lower priority

Consider the candidate's existing background.
Do not recommend learning something they already appear to know unless
they need to    strengthen it.
Use at most 300 words.
Return a practical ordered list.
Do not output internal monologue or <think> tags.
"""

    response = llm.invoke(prompt)

    return {
        "priorities": clean_llm_output(response.content)
    }

def generate_roadmap(state: RoadmapState):
    prompt = f"""
You are creating a personalized career roadmap.

Target role:
{state["target_role"]}

Skill gaps:
{state["skill_gaps"]}

Prioritized learning areas:
{state["priorities"]}

Create a practical, step-by-step roadmap for the candidate.

The roadmap should:

1. Be personalized to the candidate's current background.
2. Focus on the most important skill gaps first.
3. Build skills in a logical order.
4. Include practical projects or exercises where appropriate.
5. Avoid unnecessarily repeating skills the candidate already knows.
6. Be realistic and actionable.

Structure the roadmap into clear phases.

For each phase include:

- Main focus
- Skills/topics to learn
- Practical work or project
- Expected outcome

End with a section explaining what the candidate should be able to do after completing the roadmap.

Do not invent experience or claim the candidate already knows something
unless supported by their profile analysis.
Do not output internal monologue or <think> tags. Output only the final roadmap response.
"""

    response = llm.invoke(prompt)

    return {
        "roadmap": clean_llm_output(response.content)
    }

graph = StateGraph(RoadmapState)

graph.add_node("analyze_profile", analyze_profile)
graph.add_node("analyze_gaps", analyze_gaps)
graph.add_node("prioritize_skills", prioritize_skills)
graph.add_node("generate_roadmap", generate_roadmap)


graph.add_edge(START, "analyze_profile")
graph.add_edge("analyze_profile", "analyze_gaps")
graph.add_edge("analyze_gaps", "prioritize_skills")
graph.add_edge("prioritize_skills", "generate_roadmap")
graph.add_edge("generate_roadmap", END)

roadmap_graph = graph.compile()

