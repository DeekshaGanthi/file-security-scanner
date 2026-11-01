# Milestone 6 implementation checkpoint - November 1, 2026

The approved cloud infrastructure phase is complete. Application deployment and
the live observability/rollback demonstrations remain pending. Existing Milestone 5
application availability and security controls are preserved.

## Architecture and logging

Streamlit -> FastAPI -> private PostgreSQL/GCS, YARA and Gemini remains unchanged.
backend/logging_config.py adds one allowlisted JSON request-completion record with
timestamp, severity, service/event, route-template path, integer status, duration
and UUID. Error text is generic; headers, query strings, filenames, request bodies
and secret values are excluded. main.py integrates it, scan events use JSON,
yara_engine.py uses safe initialization logging, and Dockerfile.backend disables
duplicate Uvicorn access logs.

backend/demo.py is a separate loopback-only server reached by authorized pod exec.
It writes through PID 1 stdout for real container logging and never mounts in the
public app. Its deployed behavior remains pending. See monitoring-setup.md for
PowerShell commands and exact metric/filter/schema details.

## Cloud monitoring

Terraform created scanner_http_5xx_count, the three-chart dashboard, enabled alert
policy and authorized email channel. Actual CPU and memory time-series points were
verified for each workload. New-app JSON ingestion, isolated 200/404/503 metric
behavior, incident creation, received email and screenshots remain pending.
No controlled error or notification receipt is claimed.

Dashboard: projects/956088853573/dashboards/014b4b60-8667-45b8-8445-e7e736abae7e
Policy: projects/file-security-scanner/alertPolicies/3124806542354479175
Channel: projects/file-security-scanner/notificationChannels/1894265117624298755

## Terraform

Six existing resources imported without resource updates/deletes; ten monitoring/CI
additions created. The dedicated private versioned state bucket uses separate
bootstrap/application prefixes. Both refresh-enabled plans now report No changes,
exit 0. See terraform-coverage.md for ownership and narrow provider exceptions.
State, private tfvars and binary plans remain ignored and uncommitted.

## CI/CD and rollback

Branch-restricted GitHub WIF, deploy service account, additive IAM and namespace
RBAC are applied. Eight authorization checks verify scoped access; no user-managed
SA keys exist. Provider ID:
projects/956088853573/locations/global/workloadIdentityPools/scanner-github/providers/github

.github/workflows/milestone6-deploy.yml builds SHA-tagged images, deploys immutable
digests, checks each intended pod plus HTTPS and automatically restores verified
prior pod templates on failure. scripts/release.py preserves HPA ownership and
keeps failed deployments marked failed. Actual runs and recovery are pending.
See cicd-workflow.md and rollback-test.md.

## Current status and remaining work

17 tests pass. HTTPS 200; two ready replicas per workload; HPA/PDB and Active
certificate intact. SQL SELECT 1 passes. Docker engine unavailable locally.
Budget API returned 403; no budget configuration changed.

Next: review the tested development commit and verified provider ID, then
promote to milestone6-deploy, verify the real deployment and scan integration,
then perform the controlled 503/received notification and failed-rollout/recovery
demonstrations. Capture real screenshots/run URLs/commit SHAs. No deployment branch
push has run. Evidence and exact status: verification-report.md and evidence/README.md.
No written analysis, slides or video were created.
