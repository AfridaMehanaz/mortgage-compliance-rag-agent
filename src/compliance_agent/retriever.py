from dataclasses import dataclass

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from compliance_agent.knowledge_base import PolicyDocument
from compliance_agent.schemas import Citation


@dataclass(frozen=True)
class RetrievalResult:
    document: PolicyDocument
    score: float


class PolicyRetriever:
    def __init__(self, documents: list[PolicyDocument]) -> None:
        self.documents = documents
        corpus = [f"{doc.title}\n{' '.join(doc.tags)}\n{doc.text}" for doc in documents]
        self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        self.matrix = self.vectorizer.fit_transform(corpus)

    def search(self, query: str, top_k: int = 3) -> list[RetrievalResult]:
        query_vector = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vector, self.matrix).ravel()
        ranked = similarities.argsort()[::-1][:top_k]
        return [
            RetrievalResult(document=self.documents[index], score=float(similarities[index]))
            for index in ranked
            if similarities[index] > 0
        ]


def result_to_citation(result: RetrievalResult) -> Citation:
    text = " ".join(result.document.text.split())
    snippet = text[:280] + ("..." if len(text) > 280 else "")
    return Citation(
        document_id=result.document.document_id,
        title=result.document.title,
        snippet=snippet,
        score=round(result.score, 4),
    )

