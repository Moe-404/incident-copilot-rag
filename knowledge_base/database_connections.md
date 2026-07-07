# Database Connection Exhaustion Runbook

service: database
severity: critical

## Detection

Confirm connection-pool wait time, active connections, and rejected connections. Check database CPU and query latency to distinguish pool exhaustion from a slow or unavailable database.

## Triage

Identify the application, route, and deployment creating the most connections. Inspect long-running and idle-in-transaction sessions. Never terminate sessions until their owner, age, and business impact are understood.

## Mitigation

Stop or roll back a confirmed connection leak. For stuck non-critical sessions, follow the approved termination procedure and preserve query identifiers for analysis. Increasing the connection limit is a temporary measure only when database capacity has been verified.

## Verification

Verify that pool wait time, rejected connections, and database load remain normal for fifteen minutes. Run a synthetic transaction and confirm that application errors have stopped.
