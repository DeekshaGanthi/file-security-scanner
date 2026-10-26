# Two-slide PowerPoint content and layout specification

Exactly two slides, 16:9, white background, navy headings and teal connections.
Use Aptos or Arial. Titles 30-32 pt, labels 18-20 pt, notes 16 pt minimum.
All topology boxes and arrows should be editable PowerPoint objects.
Bundled presentation authoring/runtime tooling was unavailable in this session;
this is the complete content and precise layout fallback, not a claimed PPTX file.

## Slide 1

Title (x 0.45, y 0.25, w 12.4, h 0.7 inches):
**AI File Security Scanner — GKE Orchestration Architecture**

Public path along top (y 1.2; left-to-right horizontal arrows):

| x | w | Label |
|---:|---:|---|
| 0.5 | 1.2 | Users |
| 2.0 | 3.5 | scanner.136-69-114-222.sslip.io / HTTPS |
| 5.8 | 3.0 | Google Cloud Application Load Balancer / Google-managed TLS Active |
| 9.1 | 3.6 | GKE Ingress scanner / HTTP → HTTPS |

Cluster area (x 0.5, y 2.5, w 12.2, h 2.5): thin navy outline labelled
`scanner-gke · Autopilot · us-central1 · namespace scanner`.
Within the cluster, show a horizontal flow at y 3.2:

`frontend Service` → `Streamlit pods ×2 minimum` → `backend Service (private)` →
`FastAPI pods ×2 minimum`.

Connect Ingress down to frontend Service using orthogonal arrows. Below pod labels:
`HPA: CPU 60%, replicas 2–5 each` and `PDB: minAvailable 1 each`.
Add annotation under backend pods: `scanner-api KSA · Workload Identity Federation`.

Private resources below cluster (y 5.5, evenly spaced):

- `Cloud SQL PostgreSQL / 172.27.208.3 private / scanner_db`
- `Cloud Storage / file-security-scanner-uploads-2026 / private`
- `Secret Manager / scanner-db-password + gemini-api-key`

Connect backend pods to all three resources. Label SQL connection `default VPC / TLS`.
Frontend service account `scanner-frontend` has no cloud IAM grants.
Caption at y 6.85: `Observed: backend autoscaled 2 → 3; one deleted pod was replaced.`
Mention current count can return to two. Do not draw the old VM in the active GKE path.

Speaker notes: Streamlit calls backend server-side; browsers never resolve ClusterIP
DNS. Frontend BackendConfig: /_stcore/health, interval 10 s, timeout 5 s, healthy 1,
unhealthy 3, timeout 3600 s, generated-cookie affinity and draining 180 s.
Session affinity does not preserve lost in-memory state after pod failure.

## Slide 2

Title (x 0.5, y 0.35, w 12.3, h 0.7):
**Liveness vs. Readiness — Application Health Strategy**

Editable comparison table (x 0.6, y 1.4, w 12.1, h 3.5), two equal columns:

| Liveness | Readiness |
|---|---|
| GET /health/live | GET /health/ready |
| Checks application process | Checks application and PostgreSQL |
| No SQL, GCS, secrets or external API calls | Executes SELECT 1 without writes |
| HTTP 200 when responsive | HTTP 200 connected; HTTP 503 unavailable |
| Failure may restart container | Failure removes pod from ready Service endpoints |
| Period 10 s; timeout 3 s; failure threshold 3 | Period 10 s; timeout 10 s; failure threshold 3 |

Below table (x 0.6, y 5.2, w 12.1, h 0.9):
`Both are necessary: keep responsive processes alive during a database outage while
preventing new Service traffic from reaching pods unable to use PostgreSQL.`

At y 6.25, two lines:
`Startup probe: /health/live every 5 s, timeout 3 s, failure threshold 60.`
`Streamlit: /_stcore/health for live/ready, every 10 s, timeout 3 s, failure threshold 3.`

Speaker notes: PostgreSQL connection timeout 2 s and statement timeout 2 s. First
readiness use can resolve Secret Manager with 5 s RPC timeout; subsequent checks use
cached credentials. Readiness does not invoke Gemini or GCS. Tests proved SQL failure
returns sanitized 503 while liveness remains 200. PDB constrains eviction, not direct
deletion, and does not guarantee zero downtime.
