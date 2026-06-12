from enum import Enum

from pydantic import BaseModel, Field


class Decision(str, Enum):
    approve = "approve"
    needs_review = "needs_review"
    reject = "reject"


class CheckStatus(str, Enum):
    pass_ = "pass"
    warn = "warn"
    fail = "fail"


class AskRequest(BaseModel):
    question: str = Field(..., min_length=5, max_length=1000)
    borrower_context: dict[str, str | int | float | bool] = Field(default_factory=dict)
    top_k: int = Field(default=3, ge=1, le=8)


class Citation(BaseModel):
    document_id: str
    title: str
    snippet: str
    score: float


class ComplianceCheck(BaseModel):
    name: str
    status: CheckStatus
    reason: str


class AskResponse(BaseModel):
    answer: str
    decision: Decision
    confidence: float = Field(..., ge=0, le=1)
    citations: list[Citation]
    checks: list[ComplianceCheck]
    guardrail_flags: list[str] = Field(default_factory=list)

