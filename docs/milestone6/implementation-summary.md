# Milestone 6 implementation checkpoint - November 1, 2026

The approved cloud infrastructure phase is complete. Application deployment and
the live observability/rollback demonstrations are now verified. Required screenshot
artifacts and interactive browser UI confirmation remain pending. Existing Milestone 5
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
public app. Its real 503, log ingestion, public-route exclusion and listener shutdown
were verified. See monitoring-setup.md for
PowerShell commands and exact metric/filter/schema details.

## Cloud monitoring

Terraform created scanner_http_5xx_count, the three-chart dashboard, enabled alert
policy and authorized email channel. Actual CPU and memory time-series points were
verified for each workload. Real JSON ingestion, 200/404/503 filter behavior and DELTA error count 1
were verified. Incident 0.oeimw7fsr668 opened at 22:58:38 UTC; the authorized
recipient confirmed email receipt. Screenshot artifacts remain pending.

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
keeps failed deployments marked failed. Successful deployment and automatic recovery from the controlled failed rollout are verified.
See cicd-workflow.md and rollback-test.md.

## Current status and remaining work

17 tests pass. HTTPS 200; two ready replicas per workload; HPA/PDB and Active
certificate intact. SQL SELECT 1 and a real harmless scan passed; YARA/Gemini/GCS/history all worked. Docker builds passed in Actions.
Budget API returned 403; no budget configuration changed.

Successful run: https://github.com/DeekshaGanthi/file-security-scanner/actions/runs/41358659674
Failed/recovered run: https://github.com/DeekshaGanthi/file-security-scanner/actions/runs/41359525217
Deployed code SHA: ef751fe3b3b148b0241ffe7c991eba4b92193051.
The failure demonstration used workflow input on that same commit. See the complete
verification report and evidence index. Only manual screenshot artifacts and
interactive browser confirmation remain. No written analysis, slides or video
were created.
