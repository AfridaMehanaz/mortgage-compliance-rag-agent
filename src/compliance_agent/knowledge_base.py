from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PolicyDocument:
    document_id: str
    title: str
    text: str
    tags: tuple[str, ...]


def load_policy_documents(data_dir: Path | None = None) -> list[PolicyDocument]:
    base = data_dir or Path(__file__).resolve().parents[2] / "data" / "policies"
    documents: list[PolicyDocument] = []

    for path in sorted(base.glob("*.md")):
        raw = path.read_text(encoding="utf-8").strip()
        lines = raw.splitlines()
        title = lines[0].lstrip("# ").strip() if lines else path.stem
        tags = tuple(
            line.removeprefix("Tags:").strip().split(", ")
            for line in lines
            if line.startswith("Tags:")
        )
        flattened_tags = tuple(tags[0]) if tags else ()
        body = "\n".join(line for line in lines if not line.startswith("Tags:")).strip()
        documents.append(
            PolicyDocument(
                document_id=path.stem,
                title=title,
                text=body,
                tags=flattened_tags,
            )
        )

    if not documents:
        raise FileNotFoundError(f"No policy documents found in {base}")

    return documents

