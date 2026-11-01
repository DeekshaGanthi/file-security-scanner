# Monitoring setup and verification

Status: Terraform resources applied and API-verified November 1, 2026.
Historical baseline had no metrics/dashboards/policies/channels. Policy and email
channel are now enabled. Real CPU and memory data verified for both workloads.
The new application image, controlled 503 metric, incident and email receipt remain
pending. Resource IDs and evidence are in implementation-summary.md.
The user supplied an authorized email privately; do not put it in committed tfvars.

## Logs and controlled error

`backend/logging_config.py` emits timestamp, severity, service, event, method,
route-template path, integer HTTP status, duration and UUID request ID. Safe error
category/message are added for failures. Raw URLs, unknown paths, query strings,
headers, request bodies, filenames and exception text are not logged. Uvicorn
access logs are disabled. Scan timing and upload events use JSON too.

`backend.demo` is not mounted on the public app. Its opt-in server binds only
127.0.0.1:8001 inside an existing backend pod; forwarded headers cannot authorize
access. Namespace pod exec permission is required. It does not access the database,
GCS or Gemini. It writes JSON through `/proc/1/fd/1` into the backend container's
real stdout stream: plain `kubectl exec` stdout would bypass Cloud Logging.
The process fails if the runtime denies this file access; ingestion must be verified.
Stop the listener with Ctrl+C when testing finishes.

After the new image is deployed, in PowerShell terminal 1:

```powershell
$pod = kubectl get pods -n scanner -l app=backend -o 'jsonpath={.items[0].metadata.name}'
kubectl exec -n scanner $pod -c backend -- python -m backend.demo
```

In terminal 2, use that same pod name and a fresh UUID:

```powershell
$pod = 'COPY_EXACT_POD_NAME_FROM_TERMINAL_1'
$requestId = [guid]::NewGuid().ToString()
$probe = @"
import urllib.request, urllib.error
r = urllib.request.Request('http://127.0.0.1:8001/internal/demo/http-503', headers={'X-Request-ID':'$requestId'})
try:
    urllib.request.urlopen(r, timeout=10)
except urllib.error.HTTPError as e:
    print(e.code, e.headers.get('X-Request-ID'), e.read().decode())
"@
$encoded = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($probe))
kubectl exec -n scanner $pod -c backend -- python -c "import base64;exec(base64.b64decode('$encoded'))"
$filter = 'resource.type="k8s_container" AND resource.labels.cluster_name="scanner-gke" AND resource.labels.namespace_name="scanner" AND jsonPayload.request_id="' + $requestId + '"'
gcloud.cmd logging read $filter --project=file-security-scanner --freshness=30m --format=json
```

For controls, request public-backend `/health/live` and an unknown route using
localhost:8000 from pod exec, with separate UUIDs. Expect 200 and 404 respectively.
Verify each has exactly one completion record. Never expose port 8001 through a
Service, Ingress, or network-wide listener.

## Metric

Exact filter is `google_logging_metric.http_5xx.filter` in
`terraform/monitoring.tf`: observed `k8s_container` scope restricted to project,
region, cluster, namespace, backend container; service=backend, event=http_request,
numeric status >=500 and <600. It excludes exception-only and nonrequest events.
DELTA INT64 counter, unit 1, no high-cardinality labels.

```powershell
gcloud.cmd logging metrics describe scanner_http_5xx_count --project=file-security-scanner
gcloud.cmd monitoring dashboards list --project=file-security-scanner
```

The metric only counts new matching entries after creation. Compare one isolated
200, one 404 and one 503 against actual metric time series; allow ingestion delay
and distinguish concurrent genuine errors by log request IDs and timestamps.
Do not interpret a missing time series as a measured zero.

## Dashboard and notification

Dashboard has one-minute summed errors, CPU rate in cores, memory bytes, grouped
by backend/frontend container in the verified cluster. Alert sums errors across
five-minute aligned windows, threshold >0, duration 0s; actual triggering delay
still depends on collection/evaluation. Confirm series and incident before claiming
success. Email channel receipt must be confirmed by the recipient.

Console: select project file-security-scanner → Monitoring → Dashboards →
AI File Security Scanner — Milestone 6 Observability. Capture all three charts
with real data. Monitoring → Alerting → AI File Security Scanner — HTTP 5xx Alert:
capture condition, channel and incident. The user must provide the received email
screenshot if inbox access is unavailable; redact unrelated private information.

[Structured logging reference](https://docs.cloud.google.com/logging/docs/structured-logging).
