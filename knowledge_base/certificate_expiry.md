# TLS Certificate Expiry Runbook

service: edge
severity: critical

## Detection

Validate the certificate expiry, hostname, issuer, chain, and the endpoint actually serving the certificate. Check from an external network to avoid relying on cached or internal-only paths.

## Triage

Identify the certificate owner, renewal mechanism, secret location, and affected load balancers or ingress resources. Determine whether renewal failed or the renewed certificate was not deployed.

## Mitigation

Trigger the approved renewal workflow and deploy the certificate through secret management. Never paste private keys into chat, tickets, logs, or source control. Avoid manual replacement unless the emergency procedure requires it.

## Verification

Verify the new serial number and expiry from the public endpoint, confirm the full chain is trusted, and test every affected hostname. Monitor handshake errors after deployment.
