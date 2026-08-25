from langchain_core.tools import tool
from chains.rag import create_rag_chain
from vectorstore import get_retriever

@tool
def search_resume(question: str) -> str:
    """
    Search the uploaded resume and answer questions using only
    information contained in the resume.
    """
    if isinstance(question, dict):
        question = question.get("question") or question.get("query") or str(question)
    elif not isinstance(question, str):
        question = str(question)

    print(f"[TOOL CALL] Executing: search_resume")
    print(f"[ARGUMENT]  Query: '{question}'")

    retriever = get_retriever()
    rag_chain = create_rag_chain(retriever)

    answer = rag_chain.invoke(question)

    return answer