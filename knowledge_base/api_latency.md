# API Latency Incident Runbook

service: api
severity: high

## Detection

Confirm that the API p95 latency exceeds the service-level objective for at least five minutes. Compare request rate, error rate, CPU, memory, database connection-pool saturation, and downstream latency before declaring an incident.

## Triage

Check whether one route, tenant, or deployment version accounts for the increase. Review the latest deployment, trace slow requests, and compare application latency with database query duration. Do not restart instances until evidence identifies a resource or process problem.

## Mitigation

If the latest deployment caused the regression, pause the rollout and use the documented rollback procedure. If traffic exceeds safe capacity, scale within the approved limit and verify that latency and error rate recover. Record every action and timestamp in the incident log.

## Verification

Keep the incident open until p95 latency remains below the objective for fifteen minutes and error rate returns to baseline. Confirm recovery from an external probe, not only from an internal dashboard.
