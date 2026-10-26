# Milestone 5 progress

## Audit and implementation plan

- Working branch: `milestone5-gke`; base `1da5b1b` (Milestone 4).
- Existing untracked `backend.zip` is preserved and excluded from commits.
- FastAPI: `backend/main.py`, port 8000; Streamlit: `frontend/app.py`, port 8501.
- Streamlit makes server-side API calls. Backend can remain private on ClusterIP.
- Existing UUID temporary uploads are removed after scanning; permanent files use GCS.
- Current import-time database verification prevents independent liveness; remove it.
- No existing tests or Kubernetes files found. Dependencies are currently unpinned.
- CLI account verified: saideekshaganthi@gmail.com; project file-security-scanner.
- Existing Autopilot cluster `scanner-gke`, us-central1, RUNNING; reuse it.
- Cluster uses default VPC/subnet, Workload Identity enabled; SQL uses same VPC.
- SQL `file-scanner-postgres`: RUNNABLE, private 172.27.208.3, public IP disabled,
  encrypted connections required. Preserve schema and records.
- Registry: us-central1-docker.pkg.dev/file-security-scanner/file-security-scanner-repo.
- No external reserved IP or public DNS zone found in initial inventory.
- Docker daemon unavailable. GKE auth plugin initially missing.
- No cloud mutations to VM, SQL, bucket, secrets, or IAM have been performed.

## Sequence

1. Audit cluster workloads, resource policies, bucket, secrets, IAM, and registry.
2. Implement independent liveness and bounded SELECT 1 readiness; test outage behavior.
3. Add lazy Secret Manager access through ADC, bounded connection pooling, nonroot images,
   frontend timeouts, upload limits, and safe internal load-test tooling.
4. Create namespace, service accounts, two deployments/services, HPA, PDB, BackendConfig,
   FrontendConfig, and hostname-dependent certificate/Ingress configuration.
5. Validate code, tests, manifests, image builds; prepare deployment automation.
6. Obtain approval for workload/LB/IP/build costs and narrowly scoped IAM grants.
7. Build/publish immutable images, deploy to existing cluster, validate private SQL and GCS.
8. Configure user-selected hostname/DNS, wait for Active TLS and verify redirect.
9. Demonstrate actual HPA scaling; obtain approval before deleting one healthy pod.
10. Collect real evidence, finalize slides/analysis/video script, commit locally;
    request approval before push. Video/OneDrive/Canvas remain team submission steps.

## Pending decisions and gates

- Domain ownership/hostname and DNS provider requested from user.
- New recurring workload/load-balancer costs require approval before apply.
- Pod deletion and GitHub push require separate approval.
- No rubric item is currently verified end to end.

## Deployment observations

- User approved deployment and free sslip.io hostname; routine commands authorized.
- Existing namespace `scanner` and KSA `scanner-api` reused with existing IAM grants.
- Official GKE auth plugin installed; Docker started and both images built/published.
- Backend image smoke test passed, including import without SQL and upload bound.
- Reserved IP: 136.69.114.222; scanner.136-69-114-222.sslip.io resolves correctly.
- All manifests passed server dry run and were applied.
- Observed 2/2 backend and 2/2 frontend Ready with zero restarts.
- Load balancer reports both frontend endpoints HEALTHY.
- PDB permits one voluntary eviction per Deployment at baseline.
- HPA metrics available: initially backend 2%, frontend 3%, two replicas each.
- Explicit private SQL SELECT 1 and live/ready endpoint requests passed.
- Actual pre-test counts: scans 38, indicators 19, llm_reports 18.
- Harmless end-to-end scan initiated; waiting for external analysis result.
- HTTP redirect verified: 301 to HTTPS on the same hostname.
- Certificate still Provisioning; trusted HTTPS verification pending.
- Bounded HPA traffic test started: 180 seconds, 64 workers, health-only endpoint.

## Verification completed

- Harmless scan ID 68 persisted: LOW risk, score 0. History 39 records; SQL counts
  scans 39, indicators 19, llm_reports 18. UUID GCS object confirmed by metadata.
- Gemini returned failure; bounded diagnostic confirmed RateLimitError. No secret
  payloads printed. Preserved original Interactions API/model and added bounds.
- HPA actually scaled backend 2 to 3 at 76%/60% CPU; three Ready pods observed.
  Load results: 25,898 successes and 11,400 failures/timeouts under saturation.
- User approved one-pod deletion; script deleted backend-6c476df4f-bntr5 and observed
  new Ready backend-6c476df4f-nb697. HPA later returned baseline to two.
- Certificate and domain Active; trusted HTTPS 200 and HTTP 301 verified.
- Browser HTTPS UI and history work. UI upload automation blocked by Chrome extension
  file-URL permission; user action requested. API multipart upload already passed.
- Complete video script, deployment guide, evidence index, rubric, half-page analysis
  text and exact two-slide layout/content prepared. Packaged Office artifact runtime
  unavailable; no fabricated PPTX/DOCX or video claimed.
- Final backend image built/published with Gemini timeout/rate-limit handling and
  container smoke test; rolling update initiated.

## Final application verification

- Final backend rolling update completed; two healthy frontend/backend replicas.
- Verification script passed private SQL SELECT 1, live/ready 200, trusted HTTPS 200
  and HTTP-to-HTTPS redirect assertions.
- User enabled Chrome extension file access. Browser upload and scan succeeded.
- Browser showed risk 0/100 LOW and a successful Gemini AI report. Prior quota
  failure was transient; AI functionality is now observed working.
- Follow-up browser scan persistence and AI report evidence is collected separately.
- Confirmed browser scan ID 69 and one saved AI report; final counts 40 scans,
  19 indicators, 19 llm_reports. Private GCS UUID object verified.
- Local commit dd2a1d7 contains the implementation and actual deployment manifests.
  Secret-pattern scan flagged no files; git diff --check and six tests pass.
  Evidence text normalized to UTF-8 for repository review. Push approval pending.
- User approved GitHub push. Published milestone5-gke, verified remote commit
  7cbc89977ab1005bfa089000c83def67d4469a5c. Main remains unchanged.
