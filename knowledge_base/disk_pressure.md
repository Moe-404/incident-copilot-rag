# Node Disk Pressure Runbook

service: kubernetes
severity: critical

## Detection

Confirm the DiskPressure node condition and measure filesystem and inode usage. Identify whether container images, logs, emptyDir volumes, or application data account for growth.

## Triage

List the largest safe-to-inspect paths and correlate growth with workloads. Check pod evictions and kubelet garbage-collection events. Do not remove files whose ownership or retention requirement is unknown.

## Mitigation

Use the approved log rotation or image garbage-collection procedure. Cordon the node before disruptive maintenance and drain it only when workload disruption budgets allow. Expanding storage requires the normal infrastructure change path.

## Verification

Confirm DiskPressure clears, inode and byte usage return below warning thresholds, kubelet operations recover, and affected workloads are healthy.
