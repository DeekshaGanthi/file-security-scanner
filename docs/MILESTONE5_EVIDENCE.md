# Evidence collection

Store command output under `docs/milestone5-evidence/` and retain timestamps.
Do not capture secret payloads, kubeconfig credentials, tokens or environment dumps.

| Evidence | Capture |
|---|---|
| Cluster | gcloud container clusters describe scanner-gke --region us-central1, selected non-sensitive fields |
| Replicas | kubectl get deployments,pods -n scanner -o wide |
| Probes | backend health source, Deployment probes, local-tests.txt and container-smoke output |
| DB | SELECT 1 from backend pod; record counts before/after a harmless new scan |
| GCS | UUID object metadata from the existing bucket, never publicize bucket |
| HPA | before/load/during/after logs with metrics and replicas; no claim if unchanged |
| Recovery | approved script before/deletion/after output; video must repeat live |
| HTTPS | ManagedCertificate Active, trusted browser connection and curl headers |
| Redirect | HTTP 301 and Location https://actual-hostname/ |
| PDB | kubectl get/describe pdb -n scanner |
| Git | git log plus repository branch manifest listing after approved push |

Browser screenshots: capture GKE workloads, certificate Active, HTTPS application,
scan results, history, and redirect address bar. A screenshot of an empty Streamlit
HTML shell alone does not verify the application WebSocket or upload flow.

Run `scripts/verify-gke.ps1 -Hostname scanner.136-69-114-222.sslip.io` for baseline logs.
Review exit status and content; the script is a collector, not an automatic score.

## Collected results

- `initial-healthy.txt`, `final-healthy.txt`: two Ready replicas for each Deployment.
- `hpa-during-load.txt`, `cpu-during-load.txt`, `load-test.txt`: real 2-to-3 scaling.
- `recovery-20261025-204728/`: approved deletion and new Ready replacement.
- `certificate-active.yaml`, headers and `20261025-205608/`: Active TLS, HTTPS 200,
  redirect and post-rollout SQL/health/resource verification.
- `e2e.txt`: API scan persistence and GCS metadata matching.
- `browser-e2e.txt`: final browser scan ID 69, saved AI report, GCS object; counts
  scans 40, indicators 19, llm_reports 19.
- `cluster.json`, `load-balancer.json`: selected non-sensitive infrastructure settings.

The browser tool displayed screenshots for visual inspection but did not expose a
documented persistent image-file export in this session. Before submission, use the
browser's normal screenshot/snipping workflow to save the final HTTPS UI, certificate
Active console view and GKE workloads. Do not substitute these for the required video.
