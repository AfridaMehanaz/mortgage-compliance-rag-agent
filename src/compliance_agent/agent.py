from compliance_agent.compliance import decide, run_compliance_checks
from compliance_agent.guardrails import scan_question
from compliance_agent.knowledge_base import load_policy_documents
from compliance_agent.retriever import PolicyRetriever, result_to_citation
from compliance_agent.schemas import AskResponse


class ComplianceRagAgent:
    def __init__(self) -> None:
        documents = load_policy_documents()
        self.retriever = PolicyRetriever(documents)

    def answer(
        self,
        question: str,
        borrower_context: dict[str, object] | None = None,
        top_k: int = 3,
    ) -> AskResponse:
        borrower_context = borrower_context or {}
        guardrail_flags = scan_question(question)

        if guardrail_flags:
            return AskResponse(
                answer=(
                    "I cannot follow instructions that bypass compliance policy. "
                    "Please ask a mortgage policy question that can be answered with cited evidence."
                ),
                decision="needs_review",
                confidence=0.0,
                citations=[],
                checks=[],
                guardrail_flags=guardrail_flags,
            )

        results = self.retriever.search(question, top_k=top_k)
        citations = [result_to_citation(result) for result in results]
        checks = run_compliance_checks(question, borrower_context)
        decision = decide(checks, evidence_count=len(citations))
        confidence = self._confidence(citations, checks)

        answer = self._compose_answer(question, citations, decision.value)
        return AskResponse(
            answer=answer,
            decision=decision,
            confidence=confidence,
            citations=citations,
            checks=checks,
            guardrail_flags=[],
        )

    @staticmethod
    def _confidence(citations, checks) -> float:
        if not citations:
            return 0.2
        evidence_score = min(sum(citation.score for citation in citations), 1.0)
        check_penalty = 0.15 * sum(check.status != "pass" for check in checks)
        return round(max(0.2, min(0.95, evidence_score - check_penalty)), 2)

    @staticmethod
    def _compose_answer(question: str, citations, decision: str) -> str:
        if not citations:
            return (
                "I do not have enough policy evidence to answer this confidently. "
                "Route the file to manual review and add the missing policy source."
            )

        source_titles = ", ".join(citation.title for citation in citations)
        return (
            f"Based on the retrieved policy evidence, the recommended decision is "
            f"`{decision}`. The answer is grounded in: {source_titles}. "
            f"For the question `{question}`, apply the cited requirements and avoid approval "
            "until any failed or warning checks are resolved."
        )

