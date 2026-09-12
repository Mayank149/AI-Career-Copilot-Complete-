#Evaluation of Retriever -- Recall@4

import sys
import json
from pathlib import Path

# Add backend directory to sys.path so modules like vectorstore can be resolved
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from vectorstore import get_retriever

DATASET_PATH = Path(__file__).parent / "retrieval_dataset.json"


def load_dataset():
    with open(DATASET_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def calculate_recall(relevant_chunks, retrieved_chunks):
    relevant = set(relevant_chunks)
    retrieved = set(retrieved_chunks)

    hits = relevant.intersection(retrieved)

    return len(hits) / len(relevant)


def calculate_reciprocal_rank(relevant_chunks, retrieved_chunks):
    relevant = set(relevant_chunks)

    for rank, chunk_id in enumerate(retrieved_chunks, start=1):
        if chunk_id in relevant:
            return 1 / rank

    return 0


def evaluate():
    dataset = load_dataset()
    retriever = get_retriever()

    total_recall = 0
    total_reciprocal_rank = 0

    print("=" * 60)
    print("RAG RETRIEVAL EVALUATION")
    print("=" * 60)

    for index, item in enumerate(dataset, start=1):
        question = item["question"]
        relevant_chunks = item["relevant_chunks"]

        results = retriever.invoke(question)

        retrieved_chunks = [
            doc.metadata["chunk_id"]
            for doc in results
        ]

        recall = calculate_recall(
            relevant_chunks,
            retrieved_chunks
        )

        reciprocal_rank = calculate_reciprocal_rank(
            relevant_chunks,
            retrieved_chunks
        )

        total_recall += recall
        total_reciprocal_rank += reciprocal_rank

        print(f"\nQ{index}: {question}")
        print(f"Expected:  {relevant_chunks}")
        print(f"Retrieved: {retrieved_chunks}")
        print(f"Recall@4:  {recall:.2%}")
        print(f"RR:        {reciprocal_rank:.2f}")

    average_recall = total_recall / len(dataset)
    mrr = total_reciprocal_rank / len(dataset)

    print("\n" + "=" * 60)
    print(f"Queries:       {len(dataset)}")
    print(f"Recall@4:      {average_recall:.2%}")
    print(f"MRR@4:         {mrr:.2%}")
    print("=" * 60)


if __name__ == "__main__":
    evaluate()