from compliance_agent.knowledge_base import load_policy_documents
from compliance_agent.retriever import PolicyRetriever


EVAL_SET = [
    {
        "query": "How recent do income documents need to be?",
        "relevant_document_id": "income-verification",
    },
    {
        "query": "What debt to income ratio needs additional review?",
        "relevant_document_id": "ability-to-repay",
    },
    {
        "query": "What should we do if identity verification is missing?",
        "relevant_document_id": "identity-verification",
    },
]


def evaluate(top_k: int = 3) -> dict[str, float]:
    retriever = PolicyRetriever(load_policy_documents())
    hits = 0
    reciprocal_ranks = []

    for item in EVAL_SET:
        results = retriever.search(item["query"], top_k=top_k)
        ranked_ids = [result.document.document_id for result in results]
        if item["relevant_document_id"] in ranked_ids:
            hits += 1
            rank = ranked_ids.index(item["relevant_document_id"]) + 1
            reciprocal_ranks.append(1 / rank)
        else:
            reciprocal_ranks.append(0)

    return {
        f"recall_at_{top_k}": hits / len(EVAL_SET),
        "mrr": sum(reciprocal_ranks) / len(reciprocal_ranks),
    }


if __name__ == "__main__":
    print(evaluate())

