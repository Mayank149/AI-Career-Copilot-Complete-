from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama

llm = ChatOllama(
    model = "gemma2:2b"
)

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

