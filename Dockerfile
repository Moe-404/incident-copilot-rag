FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app
RUN addgroup --system app && adduser --system --ingroup app app

COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --upgrade pip && pip install --no-cache-dir .

COPY knowledge_base ./knowledge_base
COPY data ./data
COPY sql ./sql
RUN mkdir -p artifacts reports && chown -R app:app /app

USER app
RUN python -m runbook_rag.cli index

EXPOSE 8000
CMD ["uvicorn", "runbook_rag.api:app", "--host", "0.0.0.0", "--port", "8000"]
