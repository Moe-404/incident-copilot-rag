from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    document_id: str
    title: str
    section: str
    source: str
    service: str
    severity: str
    text: str


def _metadata(text: str, path: Path) -> tuple[str, str, str]:
    title_match = re.search(r"(?m)^#\s+(.+)$", text)
    title = title_match.group(1).strip() if title_match else path.stem.replace("_", " ").title()
    service_match = re.search(r"(?mi)^service:\s*(.+)$", text)
    severity_match = re.search(r"(?mi)^severity:\s*(.+)$", text)
    service = service_match.group(1).strip().lower() if service_match else "general"
    severity = severity_match.group(1).strip().lower() if severity_match else "unknown"
    return title, service, severity


def chunk_markdown(path: Path, max_chars: int = 1_200) -> list[Chunk]:
    raw = path.read_text(encoding="utf-8")
    title, service, severity = _metadata(raw, path)
    sections = re.split(r"(?m)^##\s+", raw)
    chunks: list[Chunk] = []
    sequence = 0
    for section_text in sections[1:]:
        lines = section_text.strip().splitlines()
        if len(lines) < 2:
            continue
        heading = lines[0].strip()
        paragraphs = [part.strip() for part in "\n".join(lines[1:]).split("\n\n") if part.strip()]
        current = ""
        for paragraph in paragraphs:
            candidate = f"{current}\n\n{paragraph}".strip()
            if current and len(candidate) > max_chars:
                sequence += 1
                chunks.append(
                    _make_chunk(path, title, heading, service, severity, current, sequence)
                )
                current = paragraph
            else:
                current = candidate
        if current:
            sequence += 1
            chunks.append(_make_chunk(path, title, heading, service, severity, current, sequence))
    return chunks


def _make_chunk(
    path: Path,
    title: str,
    section: str,
    service: str,
    severity: str,
    text: str,
    sequence: int,
) -> Chunk:
    identity = hashlib.sha256(f"{path.stem}:{section}:{text}".encode()).hexdigest()[:12]
    return Chunk(
        chunk_id=f"{path.stem}-{sequence}-{identity}",
        document_id=path.stem,
        title=title,
        section=section,
        source=f"knowledge_base/{path.name}",
        service=service,
        severity=severity,
        text=text,
    )


def load_corpus(directory: Path) -> list[Chunk]:
    chunks = [chunk for path in sorted(directory.glob("*.md")) for chunk in chunk_markdown(path)]
    if not chunks:
        raise ValueError(f"No runbook sections found in {directory}")
    return chunks
