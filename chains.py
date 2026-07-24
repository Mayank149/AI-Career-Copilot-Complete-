from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_template("""
You are an AI Career Copilot.

Answer the question only using the provided resume.

If the answer is not present, say:
"I couldn't find that information in the resume."

Resume:
{context}

Question:
{question}
""")
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)