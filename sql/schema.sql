CREATE TABLE IF NOT EXISTS query_events (
    id BIGSERIAL PRIMARY KEY,
    request_id VARCHAR(36) UNIQUE NOT NULL,
    question TEXT NOT NULL,
    service VARCHAR(64),
    generator VARCHAR(32) NOT NULL,
    latency_ms DOUBLE PRECISION NOT NULL,
    citations JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_query_events_created_at ON query_events (created_at DESC);
CREATE INDEX IF NOT EXISTS ix_query_events_service ON query_events (service);

CREATE TABLE IF NOT EXISTS feedback_events (
    id BIGSERIAL PRIMARY KEY,
    request_id VARCHAR(36) NOT NULL,
    relevant BOOLEAN NOT NULL,
    comment TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_feedback_request_id ON feedback_events (request_id);

-- Operational quality: daily relevance and latency from real user feedback.
SELECT
    DATE(q.created_at) AS day,
    COUNT(*) AS queries,
    ROUND(AVG(q.latency_ms)::numeric, 2) AS avg_latency_ms,
    ROUND(AVG(CASE WHEN f.relevant THEN 1.0 ELSE 0.0 END)::numeric, 3) AS relevance_rate
FROM query_events q
LEFT JOIN feedback_events f USING (request_id)
GROUP BY DATE(q.created_at)
ORDER BY day DESC;
