from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from graphs.resume_editor_graph import resume_editor_graph


@tool
def propose_resume_edit(instruction: str, config: RunnableConfig) -> str:
    """
    Propose a modification, addition, rewrite, or update to the candidate's resume.
    Use this tool ONLY when the user explicitly requests to edit, change, update, add to,
    rewrite, or improve any part of their resume (summary, skills, experience, projects, education, etc.).
    Do NOT use this tool for general questions, general advice, or skill gap analysis.
    """
    thread_id = config.get("configurable", {}).get("thread_id", "default")
    sub_conf = {"configurable": {"thread_id": thread_id}}

    print(f"🛠️ [TOOL propose_resume_edit] Instruction: '{instruction}' | Thread: '{thread_id}'")

    # Invoke LangGraph resume editor (runs until human_review interrupt)
    resume_editor_graph.invoke(
        {
            "thread_id": thread_id,
            "instruction": instruction,
        },
        config=sub_conf
    )

    state = resume_editor_graph.get_state(sub_conf)
    if state.tasks and any(t.interrupts for t in state.tasks):
        iv = state.tasks[0].interrupts[0].value
        return (
            f"A resume edit proposal has been prepared and presented to the user for review:\n"
            f"- Original text: {iv.get('target_original')}\n"
            f"- Proposed replacement: {iv.get('proposed_diff')}\n"
            f"- Explanation: {iv.get('explanation')}\n"
            f"Notify the user that the change has been prepared and they can review and approve it below."
        )

    return "Resume edit proposal generated."
