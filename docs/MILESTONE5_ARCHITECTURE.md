# Milestone 5 architecture and approval proposal

## Existing resources confirmed

Reuse Autopilot cluster `scanner-gke`, region `us-central1`, namespace `scanner`.
Existing KSA `scanner-api` already has resource-scoped WIF grants on both secrets
and the existing bucket. No new IAM grants are needed for the initial deployment.
Bucket grant is `roles/storage.objectUser`; the app only creates UUID objects.
A future tightening to objectCreator is possible, but existing grants are preserved.
Frontend uses a separate `scanner-frontend` KSA with no cloud IAM grants.
Node identity already has Artifact Registry reader access.

## Approved and deployed architecture

Internet → approved hostname → reserved global IPv4 `scanner-gke-ip` →
GCE external Application Load Balancer → GKE Ingress → frontend ClusterIP →
2 Streamlit pods → backend ClusterIP → 2 FastAPI pods → existing private SQL.
Backend also uses existing GCS and Secret Manager through ADC/WIF.

Backend is not publicly routed. Process health is `/health/live`; DB readiness is
`/health/ready`. Streamlit uses `/_stcore/health`. BackendConfig explicitly checks
Streamlit's own health path, has a 3600-second WebSocket/request timeout,
cookie affinity and 180-second draining. Affinity supports Streamlit sessions;
pod loss can still require reconnection and loses transient UI state.
HPA: each Deployment min 2, max 5, CPU target 60%. PDB: minAvailable 1 each.
Rolling updates: maxUnavailable 0, maxSurge 1. No persistent volumes required.
Each pod requests 250m CPU; backend 1 GiB RAM, frontend 512 MiB RAM.
Temporary uploads are pod-local, bounded at 20 MiB per upload, and removed.
No schema migration or historical record modification runs during startup.

## Cost estimate and approval scope

Planning estimates in USD, 730 hours/month, on-demand prices; billing discounts,
free credits, Autopilot admission adjustments, actual usage and taxes may differ.

| Item | Estimate / consideration |
|---|---|
| Existing cluster management | $0.10/hour ≈ $73/month before eligible $74.40 billing-account free-tier credit; already exists |
| Four baseline pods | 1 requested vCPU + 3 GiB memory, roughly $43–$60/month plus ephemeral storage |
| HPA peak (five of each) | 2.5 requested vCPU + 7.5 GiB memory; roughly 2.5× baseline while sustained |
| External Application LB | Forwarding-rule baseline around $18.25/month, plus processed bytes; allow $20–$30/month for low traffic |
| External IP | Forwarding-rule IP pricing differs from VM IP pricing; unused reservations can be charged; reserve only when deploying |
| Existing VM / Cloud SQL | Existing recurring charges continue; SQL is not recreated or resized |
| Registry / build | Storage grows with two images; prefer local Docker build, or separately approved Cloud Build usage if needed |
| GCS / Secret Manager / Gemini | Existing usage billing; one bounded end-to-end scan proposed, no AI requests during HPA test |
| DNS / certificate | sslip.io hostname has no registration/zone fee; GKE managed certificate has no separate certificate purchase |
| Egress / logs | Additional usage-based charges; cross-zone private traffic can be $0.01/GiB; public egress depends on destination |

Budget roughly **$65–$100/month of new baseline workloads and networking**, plus
existing VM/SQL/cluster charges, variable usage, build costs and HPA bursts.
This is an estimate, not a spending cap. Nothing is automatically deleted after testing.

User approved building/publishing, applying workloads, reserving the IP and creating
Ingress/LB. Images were built locally; Cloud Build was not enabled. User separately
approved one-pod recovery. Git push remains a separate approval. No domain purchased.

## Hostname options

1. Recommended first attempt: `scanner.<reserved-IP-with-dashes>.sslip.io`.
   Free public DNS resolves the embedded IP; no DNS zone required. Request an
   ordinary GKE ManagedCertificate for that exact hostname. Confirm authoritative
   DNS, CAA compatibility, Active status and trusted TLS before counting the rubric.
   Third-party DNS availability and CA issuance/rate limits remain dependencies.
2. Free delegated subdomain from a domain owner (for example a team/university
   domain): owner creates an A record. Same GKE certificate and redirect, but
   requires authorization and access to that DNS zone.
3. Purchased domain: obtain explicit registrar quote including renewal price before
   purchase. Can use registrar DNS without a paid Cloud DNS zone. Better ownership
   control, but registration is unnecessary if option 1 succeeds.

An sslip.io hostname is real public DNS but is not a domain owned by the team.
If the instructor requires ownership rather than a real hostname, confirm acceptance
or use option 2/3. A certificate imported manually does not establish the required
Google-managed `Active` evidence. No success is claimed before actual issuance.

Sources checked during implementation:
- https://cloud.google.com/kubernetes-engine/pricing
- https://cloud.google.com/vpc/pricing
- https://sslip.io/
- https://docs.cloud.google.com/kubernetes-engine/docs/how-to/managed-certs
- https://docs.cloud.google.com/kubernetes-engine/docs/how-to/ingress-configuration
- https://docs.cloud.google.com/kubernetes-engine/docs/concepts/workload-identity
