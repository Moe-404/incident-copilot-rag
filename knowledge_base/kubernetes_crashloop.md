# Kubernetes CrashLoopBackOff Runbook

service: kubernetes
severity: high

## Detection

Confirm the pod is repeatedly restarting and capture the namespace, workload, image digest, restart count, and recent events. Determine whether the failure affects one pod or the entire deployment.

## Triage

Inspect current and previous container logs, pod events, readiness and liveness probes, resource limits, mounted configuration, and secret references. Compare the failing replica with the last healthy deployment revision.

## Mitigation

If a new image or configuration caused the failure, pause the rollout and roll back to the last verified revision. Do not delete all failing pods at once because that removes evidence and may increase impact.

## Verification

Confirm that replacement pods become ready, restart counts stop increasing, probes pass, and the service responds through its normal entry point for fifteen minutes.
