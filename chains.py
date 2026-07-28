from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama
from config import LLM_MODEL

llm = ChatOllama(
    model = LLM_MODEL
)

prompt = ChatPromptTemplate.from_template("""
You are an AI Career Copilot.

Answer the user's question using ONLY the information provided in the resume context.

If the answer cannot be found in the resume, respond exactly:

"I couldn't find that information in the resume."

Do not make assumptions.
Do not use outside knowledge.

Resume:
{context}

Question:
{question}
""")

def format_docs(docs):
    context = "\n\n".join(doc.page_content for doc in docs)

    print("=" * 80)
    print("FORMATTED CONTEXT")
    print("=" * 80)
    print(context)
    print("=" * 80)

    return context

def create_rag_chain(retriever):
    return (
        {
            "context" : retriever | format_docs,
            "question" : RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )

