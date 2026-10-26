# GKE deployment and operations

## Prerequisites

PowerShell, Python 3.12+, Docker Desktop running Linux containers, gcloud CLI,
kubectl and the official gke-gcloud-auth-plugin. Use the authenticated account
saideekshaganthi@gmail.com and project file-security-scanner. All cloud changes
must remain within approved deployment scope; no default cleanup is provided.

Existing cluster: `scanner-gke`, `us-central1`, Autopilot, default VPC/subnet.
Existing namespace: `scanner`. Reuse `scanner-api` KSA. Direct WIF principal:

`principal://iam.googleapis.com/projects/956088853573/locations/global/workloadIdentityPools/file-security-scanner.svc.id.goog/subject/ns/scanner/sa/scanner-api`

Its existing resource policies grant secretAccessor on scanner-db-password and
gemini-api-key, and objectUser on file-security-scanner-uploads-2026. The frontend
KSA has no cloud resource grants. No new GSA or service account JSON key is needed.
The node identity already has Artifact Registry reader access.

## Release workflow

1. Run tests and `git diff --check`. Review for secrets; preserve `.env` and backend.zip.
2. Run `scripts/build-images.ps1 -Tag UNIQUE_RELEASE_TAG`; never reuse a release tag.
   It builds separate nonroot images, smoke-tests backend and publishes to the
   existing Artifact Registry repository. Record published digests.
3. Run `python scripts/render-k8s.py --hostname scanner.136-69-114-222.sslip.io
   --frontend-image FULL_FRONTEND_DIGEST_REFERENCE --backend-image FULL_BACKEND_DIGEST_REFERENCE`.
   The command is shown over multiple lines for readability; pass the real complete
   references. Source manifests already contain deployed digests, not placeholders.
4. Review rendered resources, then run `scripts/deploy-gke.ps1 -ManifestDirectory
   milestone5-tmp/rendered`. Script checks account/project/context prerequisites,
   performs client/server validation, applies resources and waits for rollout.
   It creates a shared Streamlit cookie-signing Secret only if missing, piping the
   generated value directly to kubectl without displaying it. Never run the secret
   generator by itself in a recorded terminal.
5. Confirm Active managed certificate and resolving DNS, run verification, and commit
   the exact deployed manifests back into k8s. Obtain approval before GitHub push.

PowerShell execution policy can prevent scripts from launching. Use an approved
per-process invocation such as `powershell.exe -NoProfile -ExecutionPolicy Bypass
-File scripts/verify-gke.ps1 -Hostname scanner.136-69-114-222.sslip.io`; do not change
the machine-wide policy.

## Existing IP, DNS and TLS

Reserved global IPv4 `scanner-gke-ip`: 136.69.114.222.
Free hostname: scanner.136-69-114-222.sslip.io. Public DNS resolves the embedded IP;
there is no purchased domain or new Cloud DNS zone. Preserve the reserved IP.
ManagedCertificate `scanner-tls` owns Google certificate
`mcrt-5289e033-04a4-42c6-8686-e84e842858ae`. It reached Active.
GCE Ingress annotation selects the GKE controller; retain it even if generic
kubectl warns it is deprecated, because GKE Ingress uses this controller annotation.
FrontendConfig redirects HTTP to HTTPS with 301. Do not disable HTTP ingress when
using this redirect. BackendConfig configures explicit Streamlit health, cookie
affinity, 3600-second connection timeout and 180-second connection draining.

## Database, secrets and storage

FastAPI connects with psycopg over TLS to 172.27.208.3:5432 in the default VPC,
database scanner_db, user scanner_app. No proxy is used and no SQL IAM grant is
required for password authentication over private IP. DB password is lazily loaded
from Secret Manager via WIF and cached in memory. Application pool: min 0/max 5
per pod, pool wait 2 s, connect 2 s, statement 2 s. Readiness uses a separate
short-lived SELECT 1 connection so it does not wait behind scan requests.
The default sslmode=require encrypts transport; it does not verify server identity
like verify-full would. This preserves the existing IP-based TLS configuration.
No migrations or writes are performed by readiness.

UUID temporary uploads are bounded to 20 MiB, stored in /tmp and removed in finally.
Permanent objects remain in the existing private GCS bucket. Backend pod root is
read-only; writable emptyDir /tmp is limited to 512 MiB. Scan persistence preserves
historical records. No VM, SQL, bucket or existing secret is deleted or recreated.

## Verification and repeatable demonstrations

Run verify-gke.ps1 for resource snapshots, SELECT 1, endpoint checks, HTTPS and redirect.
Run pod-e2e.py inside one backend pod only when a new harmless scan is intended:

```powershell
Get-Content scripts/pod-e2e.py | kubectl exec -i -n scanner deployment/backend -- python -
```

This creates one scan, one GCS object and possibly one AI report. It does not remove
the evidence afterwards. Provider rate limiting can leave a scan without AI output.

For scaling, keep a port-forward in terminal A:

```powershell
kubectl port-forward -n scanner service/backend 18000:8000
```

Terminal B: `python scripts/test-autoscaling.py --seconds 180 --workers 64`.
Terminal C: `kubectl get hpa -n scanner -w`. Save before/during/after output.
Observed test: backend 2 to 3 replicas, CPU 76%/60%, three Ready pods; then back to 2.
The saturation run produced timeouts; it demonstrates scaling, not an availability SLA.

Obtain approval before `scripts/test-pod-recovery.ps1 -Approved`. It checks context
and two Ready pods, deletes only one, and verifies a new UID becomes Ready.
Stop load first; a port-forward selecting the deleted pod will disconnect normally.
PDB governs eviction API operations and does not prevent direct deletion.

## Troubleshooting

- Pending on a new Autopilot cluster: inspect events and autoscaler logs; allow node
  provisioning. Do not create another cluster or change quotas without diagnosis.
- Readiness 503: check private VPC path and scoped secret access; never dump passwords.
- Certificate Provisioning: check DNS, address attachment, CAA and domain status;
  wait for Active. Do not use curl -k or bypass browser certificate warnings.
- Streamlit reconnect: verify generated-cookie affinity and shared cookie secret.
  In-memory UI session state is not durable across pod loss.
- Gemini: a generation diagnostic returned RateLimitError, followed by successful
  generation in the final browser scan. The application bounds retry/duration and
  reports transient rate limits safely. Do not reset keys or silently increase usage.
- Browser automation upload: Chrome ChatGPT extension requires Allow access to file
  URLs. User enabled this setting and the final browser upload/scan test passed.

## Preservation and rollback

Keep the previous immutable image digest for an approved rollout rollback. Do not
roll back schema or run historical migrations. Rollback to a known image affects
only GKE Deployments; the original VM deployment is unchanged. No automatic resource
deletion is included. Review ongoing costs after the course demonstration.
