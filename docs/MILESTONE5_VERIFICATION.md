# Verification record

## Executed locally

- Six automated tests pass: independent liveness, healthy readiness, unavailable DB
  readiness with sanitized 503, SELECT 1/no writes, pool return, manifest consistency.
- Python compileall and PowerShell parser checks pass.
- Backend Docker smoke test passes with no cloud credentials: complete application
  import, healthy liveness, mocked ready/unready, 413 upload bound before GCS access.
- Frontend Docker imports Streamlit and requests successfully.
- Docker backend and frontend images built using Python 3.12, nonroot UID 10001.

## Executed in Google Cloud

- CLI auth list/config: saideekshaganthi@gmail.com, project file-security-scanner.
- GKE scanner-gke RUNNING, us-central1, Autopilot; kubectl namespace access succeeds.
- SQL file-scanner-postgres RUNNABLE, private IP only; no schema modifications.
- Bucket private access prevention enforced and uniform access enabled.
- Existing scanner/scanner-api WIF grants verified on bucket and both secrets.
- Reserved IP scanner-gke-ip: 136.69.114.222.
- DNS scanner.136-69-114-222.sslip.io resolves to 136.69.114.222.
- Services, Ingress, BackendConfig, FrontendConfig and ManagedCertificate pass
  server-side dry run and were applied. Ingress received reserved IP.
- Certificate initially Provisioning. This does not count as valid HTTPS evidence.

## Subsequent observed results

- Both Deployments reached 2/2 Ready with zero restarts. Both external LB frontend
  endpoints reported HEALTHY. Dedicated backend/frontend Services have correct endpoints.
- Private PostgreSQL SELECT 1 passed inside backend pod. Live and ready returned 200.
- Before harmless scan: scans 38, indicators 19, llm_reports 18. After scan: 39, 19, 18.
  New scan ID 68, LOW risk, score 0. History returned 39 records including existing data.
- Uploaded harmless file stored as uploads/7ba5e00d-e4a2-4874-ac65-315f1e2ab904 in the
  existing private bucket. Test filename metadata matched exactly one object.
- Gemini generation failed. A subsequent bounded diagnostic returned RateLimitError;
  model listing authenticated successfully. A generateContent check of an older model
  returned 404, so the application keeps its existing Interactions API/model.
- Backend health-only load: 180 seconds, 64 workers, 25,898 successful requests and
  11,400 failures/timeouts. HPA measured 76% CPU versus 60% target, automatically
  increased backend replicas 2 to 3, with all three Ready. Later it returned to 2.
  This demonstrates scaling under saturation, not zero failures or a throughput SLA.
- Approved deletion of backend-6c476df4f-bntr5 produced a Ready new UID/pod
  backend-6c476df4f-nb697 within the observed script run. HPA later removed excess
  capacity. See recovery directory for actual before/deletion/after evidence.
- ManagedCertificate scanner-tls and its domain reached Active; trusted curl HTTPS
  returned 200 without insecure flags. HTTP returned 301 with Location
  https://scanner.136-69-114-222.sslip.io:443/.
- Browser loaded the real Streamlit UI over HTTPS without a certificate warning.
  Clicking Load Scan History displayed the new test scan and historical rows.
- Final backend update adds a 30-second timeout and one SDK retry attempt, with safe
  rate-limit messaging. Image smoke test verified the new exception path.

## Final browser test

After the user enabled extension file access, browser upload of the 77-byte harmless
browser-verification.txt succeeded over HTTPS. Clicking Scan File displayed Scan
completed, risk 0/100 LOW, static analysis and a successful Gemini report with the
required sections. The earlier rate limit was transient. Read-only SQL/GCS follow-up
is saved in browser-e2e.txt, including confirmation of a persisted AI report.
Browser scan ID 69 has one saved AI report; final counts are scans 40, indicators 19,
llm_reports 19. Its private GCS object is uploads/86717b32-9512-4e5d-b352-d77c09801c04.
The final backend rolling update completed with two Ready replicas. Final verification
script passed SELECT 1, both health endpoints, trusted HTTPS and redirect assertions.

## Remaining limits

- Gemini can rate-limit requests; successful UI generation was subsequently observed.
- Browser upload permission blocker was resolved by the user; upload-through-UI passed.
- Required live video must be recorded by the team; the earlier test is not a recording.
- Packaged artifact dependency loader/runtime is not available in this tool session.
  Full two-slide content/layout and half-page analysis text are provided as the
  explicitly permitted fallback, without claiming a generated PPTX or DOCX.
- Git commit/push status is recorded separately in the implementation report.
