from fastapi.testclient import TestClient

from compliance_agent.api import app


def test_health() -> None:
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ask() -> None:
    client = TestClient(app)

    response = client.post(
        "/ask",
        json={
            "question": "What happens when debt to income ratio is 46 percent?",
            "borrower_context": {"debt_to_income_ratio": 46},
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["decision"] == "needs_review"
    assert body["citations"]

