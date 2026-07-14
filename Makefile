.PHONY: install index evaluate test lint run compose-up compose-down

install:
	python -m pip install -e ".[dev,mlops]"

index:
	python -m runbook_rag.cli index

evaluate: index
	python -m runbook_rag.cli evaluate --min-recall 0.8

test:
	pytest --cov=runbook_rag --cov-report=term-missing

lint:
	ruff check src tests

run:
	uvicorn runbook_rag.api:app --host 0.0.0.0 --port 8000 --reload

compose-up:
	docker compose up --build

compose-down:
	docker compose down
