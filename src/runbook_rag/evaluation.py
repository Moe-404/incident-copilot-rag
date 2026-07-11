from __future__ import annotations

import json
import math
import random
import time
from pathlib import Path

import numpy as np

from runbook_rag.retrieval import HybridRetriever


def _bootstrap_ci(values: list[float], seed: int = 42, samples: int = 2_000) -> tuple[float, float]:
    generator = random.Random(seed)
    bootstrapped = [
        sum(generator.choice(values) for _ in values) / len(values) for _ in range(samples)
    ]
    return float(np.percentile(bootstrapped, 2.5)), float(np.percentile(bootstrapped, 97.5))


def evaluate(retriever: HybridRetriever, cases: list[dict], top_k: int = 4) -> dict:
    recalls: list[float] = []
    reciprocal_ranks: list[float] = []
    ndcgs: list[float] = []
    latencies: list[float] = []
    for case in cases:
        started = time.perf_counter()
        results = retriever.search(case["question"], top_k=top_k, service=case.get("service"))
        latencies.append((time.perf_counter() - started) * 1_000)
        returned = list(dict.fromkeys(result.chunk.document_id for result in results))
        expected = set(case["relevant_documents"])
        relevant_ranks = [rank for rank, doc in enumerate(returned, 1) if doc in expected]
        recalls.append(float(bool(relevant_ranks)))
        reciprocal_ranks.append(1 / min(relevant_ranks) if relevant_ranks else 0.0)
        dcg = sum(1 / math.log2(rank + 1) for rank in relevant_ranks)
        ideal = sum(1 / math.log2(rank + 1) for rank in range(1, min(len(expected), top_k) + 1))
        ndcgs.append(dcg / ideal if ideal else 0.0)
    if not cases:
        raise ValueError("evaluation dataset is empty")
    low, high = _bootstrap_ci(recalls)
    return {
        "cases": len(cases),
        "top_k": top_k,
        "recall_at_k": float(np.mean(recalls)),
        "recall_at_k_ci95_low": low,
        "recall_at_k_ci95_high": high,
        "mrr": float(np.mean(reciprocal_ranks)),
        "ndcg_at_k": float(np.mean(ndcgs)),
        "latency_ms_p50": float(np.percentile(latencies, 50)),
        "latency_ms_p95": float(np.percentile(latencies, 95)),
    }


def load_cases(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
