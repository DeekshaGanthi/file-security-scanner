# Milestone 5 implementation report

## Outcome

Working public GKE application: https://scanner.136-69-114-222.sslip.io/

The deployment runs separate Streamlit/FastAPI replicas, replaces deleted pods,
actually autoscales under load, uses distinct health checks, and serves trusted
Google-managed HTTPS with HTTP redirect. Existing Milestone 4 resources were preserved.
The team must still record the required live video and complete OneDrive/Canvas.

## Deployed resources

| Resource | Actual configuration |
|---|---|
| Project / account | file-security-scanner / saideekshaganthi@gmail.com |
| Cluster / location | scanner-gke / us-central1 / Autopilot (pre-existing) |
| Namespace | scanner (pre-existing) |
| Deployments | frontend, backend; two minimum each |
| Services | frontend:8501, backend:8000; both ClusterIP |
| Ingress | scanner; GCE controller; public route only to frontend |
| Load balancer URL map | k8s2-um-nb6cca9e-scanner-scanner-lhn1ykxg |
| Static IP | scanner-gke-ip / 136.69.114.222 |
| Hostname | scanner.136-69-114-222.sslip.io |
| Certificate | scanner-tls / mcrt-5289e033-04a4-42c6-8686-e84e842858ae / Active |
| FrontendConfig | https-redirect / HTTP 301 |
| BackendConfig | frontend / Streamlit health, 3600 s timeout, cookie affinity, 180 s draining |
| HPA | backend, frontend; CPU 60%, min 2, max 5 |
| PDB | backend, frontend; minAvailable 1 |
| Backend identity | scanner/scanner-api, existing direct WIF resource grants |
| Frontend identity | scanner/scanner-frontend, no cloud resource IAM grants |
| SQL | file-scanner-postgres, private 172.27.208.3, scanner_db, TLS/password auth |
| GCS / secrets | Original uploads bucket and two original secrets |

Final backend digest: `sha256:1b8b8d4df689fb7f5d9f345fd82f5276f49e7c49b9ac290bbbef869b83214730`.
Frontend digest: `sha256:d82a4f0e39680cccfd87e82a7b7bb6821ef9cde84924447ecb4b4cd378cfa2f3`.
Both use the existing us-central1 Artifact Registry repository.

## Application and automation changes

- Removed import-time DB dependency; preserved existing schema and functions.
- Added /health/live (no dependencies) and /health/ready (SELECT 1, sanitized 503).
- Added bounded psycopg pooling, TLS, SQL timeouts and graceful pool shutdown.
- Added cached Secret Manager access through ADC/WIF; no keys downloaded or secrets
  in source/manifests. Frontend receives only a shared Kubernetes cookie secret.
- Added nonroot separate Dockerfiles, read-only pod roots and bounded writable /tmp.
- Enforced 20 MiB upload bound; retained private GCS and temporary-file cleanup.
- Added frontend HTTP timeouts/status checks and bounded Gemini retries/timeouts.
- Added tests, build/render/deploy/verify/load/recovery scripts and evidence collection.

Manifests in k8s: namespace, two service accounts, two Deployments, two Services,
two HPAs, two PDBs, Ingress, ManagedCertificate, BackendConfig and FrontendConfig.
All contain the actual deployment values. No placeholder-only final manifests.

## Actual test results

| Check | Result |
|---|---|
| Local tests | Six pass; container smoke additionally verifies upload limit and Gemini error sanitization |
| Replicas | Two Ready frontend and backend pods, zero restarts at final verification |
| Health / SQL | Live 200, DB-ready 200, SELECT 1 from running pod; mocked SQL failure 503 while live stays 200 |
| Upload / scan / risk | API and real HTTPS browser upload/scan pass; harmless sample 0/100 LOW |
| Historical data | Preserved; initial live count 38 scans, 19 indicators, 18 AI reports |
| GCS / SQL persistence | New scan/UUID object verified; browser follow-up in browser-e2e.txt |
| Gemini | Initial transient rate limit; final browser scan displayed a successful report |
| Autoscaling | Actual backend 2 to 3 at 76% CPU/60% target; three Ready; later back to 2 |
| Load quality | 25,898 successes, 11,400 failures/timeouts during deliberate saturation; no zero-error claim |
| Pod replacement | Approved one-pod deletion; new Ready replacement observed |
| PDB | Both selectors correct; minAvailable 1, one allowed disruption at baseline |
| HTTPS / redirect | Certificate Active, trusted HTTPS 200, HTTP 301 to HTTPS |
| Browser | UI, history, upload, results and AI report observed through HTTPS |

## Evidence and submission materials

Command evidence is under docs/milestone5-evidence: initial/final replicas, HPA load
and CPU, recovery before/deletion/after, Active certificate, curl headers, SQL/GCS
and browser scan persistence, cluster settings and LB configuration. Screenshots
were inspected in the browser tool; persistent exported screenshot files were not
available through its documented capture interface. Capture final browser/console
screenshots manually following MILESTONE5_EVIDENCE.md before submission.

Complete ten-minute narration/commands/troubleshooting script is in
MILESTONE5_VIDEO_SCRIPT.md. Exact two-slide content and layout is provided in
Milestone5_Orchestrate_Expose_SLIDES.md; half-page analysis is in
Milestone5_PDB_Analysis.md. The packaged Office authoring runtime/dependency loader
is unavailable in this session, so these are the user-permitted content fallbacks,
not claimed PPTX/DOCX files. Export the two slides and analysis with Office before
submission. No video, OneDrive upload/sharing or Canvas submission is claimed.

## Git and costs

Feature branch: milestone5-gke. Implementation commit: dd2a1d7, 81 files changed.
All required manifests, source changes, scripts, tests and actual evidence are locally
committed. A final documentation/evidence-encoding follow-up follows that commit.
GitHub push requires user approval and is pending. Main is not merged; no force-push.
Existing backend.zip and .env are preserved and excluded.

New baseline workloads/networking estimated $65-$100/month plus usage and existing
resource charges. Cluster management is $0.10/hour before eligible credits; VM and
SQL continue billing. HPA bursts, storage, logging, builds and egress add usage charges.
No paid domain or additional cluster created. Resources are retained after testing.
Detailed assumptions and official price sources: MILESTONE5_ARCHITECTURE.md.

## Remaining work and rubric

Obtain push approval, then publish the reviewed local branch. Export Office
materials, capture final screenshots, record the ten-minute camera-on demonstration,
upload to OneDrive, share with all three instructors and submit its link in Canvas.
The team must repeat recovery and HPA live on video. See MILESTONE5_RUBRIC.md for
evidence-based criterion status; no final grading score or full completion is claimed.
