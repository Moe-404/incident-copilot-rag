from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from runbook_rag.config import PROJECT_ROOT
from runbook_rag.evaluation import evaluate, load_cases
from runbook_rag.retrieval import HybridRetriever, build_index


def build_command(args) -> None:
    print(json.dumps(build_index(args.knowledge_dir, args.output), indent=2))


def evaluate_command(args) -> None:
    metrics = evaluate(HybridRetriever.load(args.index), load_cases(args.dataset), args.top_k)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    if os.getenv("MLFLOW_TRACKING_URI"):
        import mlflow

        mlflow.set_experiment("incident-copilot-retrieval")
        with mlflow.start_run():
            mlflow.log_param("retriever", "word-char-tfidf-rrf")
            mlflow.log_param("top_k", args.top_k)
            mlflow.log_metrics({key: value for key, value in metrics.items() if key != "cases"})
            mlflow.log_artifact(args.output)
    print(json.dumps(metrics, indent=2))
    if metrics["recall_at_k"] < args.min_recall:
        raise SystemExit(
            f"Recall@{args.top_k}={metrics['recall_at_k']:.3f} is below {args.min_recall}"
        )


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="Incident Copilot RAG MLOps pipeline")
    commands = root.add_subparsers(required=True)

    build = commands.add_parser("index", help="Build a versioned hybrid retrieval index")
    build.add_argument("--knowledge-dir", type=Path, default=PROJECT_ROOT / "knowledge_base")
    build.add_argument("--output", type=Path, default=PROJECT_ROOT / "artifacts/rag_index.joblib")
    build.set_defaults(function=build_command)

    evaluation = commands.add_parser("evaluate", help="Run the retrieval quality gate")
    evaluation.add_argument(
        "--index", type=Path, default=PROJECT_ROOT / "artifacts/rag_index.joblib"
    )
    evaluation.add_argument("--dataset", type=Path, default=PROJECT_ROOT / "data/evaluation.jsonl")
    evaluation.add_argument("--output", type=Path, default=PROJECT_ROOT / "reports/metrics.json")
    evaluation.add_argument("--top-k", type=int, default=4)
    evaluation.add_argument("--min-recall", type=float, default=0.8)
    evaluation.set_defaults(function=evaluate_command)
    return root


def main() -> None:
    args = parser().parse_args()
    args.function(args)


if __name__ == "__main__":
    main()
