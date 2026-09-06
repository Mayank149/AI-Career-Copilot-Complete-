import json
import re
from typing import TypedDict, Optional
from pathlib import Path
from pydantic import BaseModel, Field

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command

import config
from services.llm_service import get_llm
from services.resume_service import (
    get_resume_text,
    backup_original_resume,
    restore_original_resume,
    has_original_backup
)
from services.pdf_generator import generate_resume_pdf
from vectorstore import reindex_active_resume


class EditProposalSchema(BaseModel):
    target_original: str = Field(description="The exact text, sentence, or bullet point in the current resume to be replaced. Must appear in the resume.")
    proposed_diff: str = Field(description="The rewritten, improved replacement text.")
    explanation: str = Field(description="A brief explanation of why this change improves the resume.")


class ResumeEditorState(TypedDict):
    thread_id: str
    instruction: str
    original_resume_text: str
    target_original: Optional[str]
    proposed_diff: Optional[str]
    explanation: Optional[str]
    full_new_text: Optional[str]
    status: str  # "proposed", "approved", "rejected", "cancelled"
    feedback: Optional[str]
    message: str


def node_propose_edit(state: ResumeEditorState) -> dict:
    resume_text = state.get("original_resume_text") or get_resume_text()
    llm = get_llm()

    feedback_context = f"\nUser feedback on previous attempt: {state.get('feedback')}" if state.get("feedback") else ""

    prompt = f"""
You are an expert resume editor and ATS optimizer.
A user wants to make a specific change to their resume.

User Request: "{state['instruction']}"{feedback_context}

Current Resume:
\"\"\"
{resume_text}
\"\"\"

Analyze the resume and the user request:
1. Locate the EXACT sentence, bullet point, line, or paragraph that needs to be modified or updated. If the user wants to add a skill or experience, select the existing section line (e.g. SKILLS or specific job title) where it belongs.
2. Formulate the improved, professional, high-impact replacement text.
3. Provide a clear 1-2 sentence explanation of why this change improves ATS scoring or visual impact.

Return a JSON object with exactly these keys:
- "target_original": The exact substring currently in the resume to replace. (Must match text from the resume verbatim).
- "proposed_diff": The new improved replacement text.
- "explanation": Why this change is better.

Return ONLY valid JSON. Do not include markdown fences or any extra text.
"""
    response = llm.invoke(prompt)
    content = response.content.strip()

    # Clean markdown json code blocks if present
    content = re.sub(r"^```json\s*", "", content)
    content = re.sub(r"^```\s*", "", content)
    content = re.sub(r"\s*```$", "", content)

    try:
        data = json.loads(content)
        target_orig = data.get("target_original", "").strip()
        proposed = data.get("proposed_diff", "").strip()
        explanation = data.get("explanation", "").strip()
    except Exception:
        target_orig = ""
        proposed = content
        explanation = "Direct edit proposed based on user request."

    # Compute full_new_text
    if target_orig and target_orig in resume_text:
        full_new = resume_text.replace(target_orig, proposed, 1)
    else:
        # Fallback if exact match wasn't found verbatim: use heuristic or append
        target_orig = target_orig or "Selected resume section"
        full_new = resume_text + "\n" + proposed

    return {
        "original_resume_text": resume_text,
        "target_original": target_orig,
        "proposed_diff": proposed,
        "explanation": explanation,
        "full_new_text": full_new,
        "status": "proposed",
        "message": f"I've prepared the proposed change for your review."
    }


def node_human_review(state: ResumeEditorState) -> dict:
    """
    Human-in-the-Loop Interrupt Node.
    Pauses execution and sends the proposal payload to the human.
    Resumes when human responds with 'approve', 'reject', or 'cancel'.
    """
    review_data = {
        "type": "resume_edit_proposal",
        "target_original": state["target_original"],
        "proposed_diff": state["proposed_diff"],
        "explanation": state["explanation"],
        "status": "awaiting_approval"
    }

    # Interrupt graph execution and wait for human decision
    human_response = interrupt(review_data)

    decision = "cancel"
    feedback = None

    if isinstance(human_response, dict):
        decision = human_response.get("action", "cancel").lower().strip()
        feedback = human_response.get("feedback")
    elif isinstance(human_response, str):
        decision = human_response.lower().strip()

    if decision in ["approve", "approved", "yes", "accept", "apply"]:
        return {"status": "approved"}
    elif decision in ["reject", "rejected", "refine", "adjust"]:
        return {
            "status": "rejected",
            "feedback": feedback or "Please refine the change to better match expectations."
        }
    else:
        return {"status": "cancelled"}


def node_apply_change(state: ResumeEditorState) -> dict:
    """
    Applies the approved change:
    1. Backs up original resume.pdf as resume_original.pdf
    2. Overwrites resume.pdf with the compiled new PDF
    3. Re-indexes the ChromaDB vector store
    """
    resume_path = Path(config.UPLOAD_DIR) / "resume.pdf"

    # Backup original before overwriting
    backup_original_resume()

    # Generate new PDF with updated text
    generate_resume_pdf(state["full_new_text"], resume_path)

    # Re-index vector store so RAG and tools immediately use new resume
    try:
        reindex_active_resume()
    except Exception as e:
        print(f"[WARN] Vector store reindexing skipped or failed: {e}")

    return {
        "status": "completed",
        "message": (
            "✅ **Resume updated successfully!**\n\n"
            "The changes have been applied to your active resume and re-indexed in memory. "
            "All future ATS checks, skill gap analyses, and questions will now use your updated resume.\n\n"
            "• You can download the new PDF using the button below.\n"
            "• If you ever want to revert back, you can restore your original resume at any time."
        )
    }


def node_cancel(state: ResumeEditorState) -> dict:
    return {
        "status": "cancelled",
        "message": "🚫 **Edit cancelled.** No changes were made to your resume. Your current resume remains active."
    }


def route_decision(state: ResumeEditorState) -> str:
    status = state.get("status")
    if status == "approved":
        return "apply_change"
    elif status == "rejected":
        return "propose_edit"
    else:
        return "cancel"


# Build LangGraph workflow
builder = StateGraph(ResumeEditorState)

builder.add_node("propose_edit", node_propose_edit)
builder.add_node("human_review", node_human_review)
builder.add_node("apply_change", node_apply_change)
builder.add_node("cancel", node_cancel)

builder.add_edge(START, "propose_edit")
builder.add_edge("propose_edit", "human_review")
builder.add_conditional_edges(
    "human_review",
    route_decision,
    {
        "apply_change": "apply_change",
        "propose_edit": "propose_edit",
        "cancel": "cancel"
    }
)
builder.add_edge("apply_change", END)
builder.add_edge("cancel", END)

editor_memory = MemorySaver()
resume_editor_graph = builder.compile(checkpointer=editor_memory)
