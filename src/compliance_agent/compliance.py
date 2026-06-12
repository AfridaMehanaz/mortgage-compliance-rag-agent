from compliance_agent.schemas import CheckStatus, ComplianceCheck, Decision


def run_compliance_checks(question: str, borrower_context: dict[str, object]) -> list[ComplianceCheck]:
    lowered = question.lower()
    checks: list[ComplianceCheck] = []

    doc_age = borrower_context.get("income_doc_age_days")
    if isinstance(doc_age, int | float):
        status = CheckStatus.pass_ if doc_age <= 90 else CheckStatus.fail
        reason = (
            f"Income document age is {doc_age} days; policy maximum is 90 days."
            if status == CheckStatus.fail
            else f"Income document age is {doc_age} days and is within policy."
        )
        checks.append(ComplianceCheck(name="income_document_freshness", status=status, reason=reason))
    elif "older than 90" in lowered or "expired income" in lowered:
        checks.append(
            ComplianceCheck(
                name="income_document_freshness",
                status=CheckStatus.fail,
                reason="The question references income documents older than the 90-day limit.",
            )
        )

    dti = borrower_context.get("debt_to_income_ratio")
    if isinstance(dti, int | float):
        status = CheckStatus.pass_ if dti <= 43 else CheckStatus.warn
        checks.append(
            ComplianceCheck(
                name="debt_to_income_threshold",
                status=status,
                reason=f"DTI is {dti}%; standard review threshold is 43%.",
            )
        )

    if "missing id" in lowered or borrower_context.get("identity_verified") is False:
        checks.append(
            ComplianceCheck(
                name="identity_verification",
                status=CheckStatus.fail,
                reason="Identity verification must be complete before approval.",
            )
        )

    if not checks:
        checks.append(
            ComplianceCheck(
                name="manual_underwriter_review",
                status=CheckStatus.warn,
                reason="No deterministic rule was triggered; cite policy and route to review if uncertain.",
            )
        )

    return checks


def decide(checks: list[ComplianceCheck], evidence_count: int) -> Decision:
    if any(check.status == CheckStatus.fail for check in checks):
        return Decision.needs_review
    if evidence_count == 0:
        return Decision.needs_review
    if any(check.status == CheckStatus.warn for check in checks):
        return Decision.needs_review
    return Decision.approve

