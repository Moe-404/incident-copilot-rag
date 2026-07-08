from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from runbook_rag.chunking import Chunk, load_corpus


@dataclass(frozen=True)
class SearchResult:
    chunk: Chunk
    score: float


class HybridRetriever:
    """Word and character TF-IDF combined with reciprocal-rank fusion."""

    def __init__(
        self, chunks: list[Chunk], word_vectorizer, word_matrix, char_vectorizer, char_matrix
    ):
        self.chunks = chunks
        self.word_vectorizer = word_vectorizer
        self.word_matrix = word_matrix
        self.char_vectorizer = char_vectorizer
        self.char_matrix = char_matrix
        self._cache: dict[tuple, list[SearchResult]] = {}

    @classmethod
    def build(cls, chunks: list[Chunk]) -> HybridRetriever:
        documents = [f"{c.title} {c.section} {c.service} {c.text}" for c in chunks]
        word = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), sublinear_tf=True)
        char = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=1, sublinear_tf=True)
        return cls(chunks, word, word.fit_transform(documents), char, char.fit_transform(documents))

    def search(
        self,
        query: str,
        top_k: int = 4,
        min_score: float = 0.01,
        service: str | None = None,
    ) -> list[SearchResult]:
        if not query.strip() or top_k < 1:
            return []
        cache_key = (query.strip().lower(), top_k, min_score, service)
        if cache_key in self._cache:
            return self._cache[cache_key]
        word_scores = cosine_similarity(self.word_vectorizer.transform([query]), self.word_matrix)[
            0
        ]
        char_scores = cosine_similarity(self.char_vectorizer.transform([query]), self.char_matrix)[
            0
        ]
        word_ranks = np.argsort(np.argsort(-word_scores)) + 1
        char_ranks = np.argsort(np.argsort(-char_scores)) + 1
        rrf_scores = 1 / (60 + word_ranks) + 1 / (60 + char_ranks)
        candidates = [
            index
            for index in np.argsort(-rrf_scores)
            if service is None or self.chunks[index].service == service.lower()
        ]
        results = []
        for index in candidates[:top_k]:
            relevance = float((word_scores[index] + char_scores[index]) / 2)
            if relevance >= min_score:
                results.append(SearchResult(self.chunks[index], relevance))
        if len(self._cache) >= 256:
            self._cache.pop(next(iter(self._cache)))
        self._cache[cache_key] = results
        return results

    def save(self, path: Path, manifest: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({"retriever": self, "manifest": manifest}, path)

    @classmethod
    def load(cls, path: Path) -> HybridRetriever:
        return joblib.load(path)["retriever"]


def corpus_sha256(directory: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(directory.glob("*.md")):
        digest.update(path.name.encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def build_index(knowledge_dir: Path, output_path: Path) -> dict:
    chunks = load_corpus(knowledge_dir)
    manifest = {
        "created_at": datetime.now(UTC).isoformat(),
        "corpus_sha256": corpus_sha256(knowledge_dir),
        "chunk_count": len(chunks),
        "retriever": "word-char-tfidf-rrf",
    }
    HybridRetriever.build(chunks).save(output_path, manifest)
    output_path.with_suffix(".json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest
