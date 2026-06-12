from fastapi import FastAPI

from compliance_agent.agent import ComplianceRagAgent
from compliance_agent.schemas import AskRequest, AskResponse

app = FastAPI(
    title="Mortgage Compliance RAG Agent",
    version="0.1.0",
    description="Cited mortgage policy assistant with compliance checks and guardrails.",
)
agent = ComplianceRagAgent()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    return agent.answer(
        question=request.question,
        borrower_context=request.borrower_context,
        top_k=request.top_k,
    )


@app.get("/metrics")
def metrics() -> dict[str, int | str]:
    return {
        "service": "mortgage-compliance-rag-agent",
        "policy_documents_loaded": len(agent.retriever.documents),
    }

