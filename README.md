# Mortgage Compliance RAG Agent

Production-style RAG agent for mortgage compliance Q&A — source citations, LLM guardrails, RAGAS evaluation, and CI quality gates.

## Architecture

```
User question
      │
      ▼
┌─────────────────────────────────────────────────────┐
│              Compliance RAG Agent                   │
│                                                     │
│  ┌── RETRIEVAL ──────────────────────────────────┐  │
│  │  Query → Pinecone / FAISS vector search       │  │
│  │  Top-K chunks + source metadata retrieved     │  │
│  │  Hybrid rerank (vector + BM25)                │  │
│  └───────────────────────────────────────────────┘  │
│                      │                              │
│  ┌── GUARDRAILS ─────────────────────────────────┐  │
│  │  Input:  topic filter, PII check              │  │
│  │  Output: hallucination check, citation verify │  │
│  └───────────────────────────────────────────────┘  │
│                      │                              │
│  ┌── GENERATION ─────────────────────────────────┐  │
│  │  LLM answers grounded only on retrieved docs  │  │
│  │  Response includes: answer + source citations │  │
│  └───────────────────────────────────────────────┘  │
│                      │                              │
│  ┌── EVALUATION ─────────────────────────────────┐  │
│  │  RAGAS metrics: faithfulness, context recall  │  │
│  │  CI gate: blocks merge if scores drop         │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
      │
      ▼
FastAPI endpoint  →  answer + citations + confidence
```

## Features

- **Grounded answers** — LLM responds only from retrieved mortgage compliance docs; no hallucination
- **Source citations** — every answer includes doc title, section and page reference
- **Guardrails** — input topic filter + output hallucination detection
- **RAGAS evaluation** — faithfulness and context recall scored on golden Q&A set
- **CI quality gate** — GitHub Actions blocks merge if RAGAS scores drop below threshold
- **FastAPI** — REST endpoint with structured response schema (Pydantic)
- **Provider-agnostic** — swap `LLM_BASE_URL` for any OpenAI-compatible API

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edit .env: set LLM_API_KEY
```

## Usage

```bash
# Seed vector store with compliance docs
python3 data/seed_docs.py

# Start API
uvicorn src.api:app --reload

# Streamlit UI
streamlit run app.py
```

## Evaluation

```bash
python3 evals/run_ragas.py
```

Scores faithfulness and context recall against golden Q&A pairs. CI fails if either drops below threshold.

## Project Structure

```
mortgage-compliance-rag-agent/
  src/
    rag_pipeline.py    # retrieval + rerank + generation
    guardrails.py      # input/output safety checks
    api.py             # FastAPI endpoint
    llm_client.py      # provider-agnostic LLM client
  data/
    seed_docs.py       # load compliance docs into vector store
  evals/
    run_ragas.py       # RAGAS faithfulness + context recall
    golden_dataset.jsonl
  .github/workflows/
    ci.yml             # runs evals on every push
  app.py               # Streamlit UI
  .env.example
  requirements.txt
```
