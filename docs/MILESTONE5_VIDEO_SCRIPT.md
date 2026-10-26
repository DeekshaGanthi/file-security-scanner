# Ten-minute demonstration script

Every presenting team member must keep their camera on during their portion.
The team records this video; no recording is claimed by the implementation agent.
Use the actual current output. Rehearse HPA reaction time before recording.
Do not substitute screenshots for live replacement or actual replica increase.

## Preparation before recording

Confirm the rubric evidence first. Certificate must be Active, four baseline pods
Ready, backend connected to SQL, HTTPS working, required files pushed after approval.
Use three terminals: controls, pod/HPA watch, and bounded load. Obtain approval for
one backend pod deletion. Keep the browser at the final HTTPS URL and slides ready.
Have a small harmless text file ready; one scan invokes Gemini and stores a new row.
Do not show .env, tokens, kubectl secrets, full pod environment or Secret Manager payloads.

```powershell
gcloud.cmd config get-value project
kubectl config current-context
kubectl get deployments,pods,hpa,pdb,managedcertificate -n scanner
kubectl port-forward -n scanner service/backend 18000:8000
```

Keep port-forward in its own terminal. It selects one pod; restart it if that pod is
deleted or replaced. This is useful for driving one pod's CPU while HPA observes the
Deployment average. It does not prove Service load distribution.

## 0:00–1:00 Introduction (60 seconds)

Narration: “We built AI File Security Scanner with Streamlit and FastAPI. Milestone 4
ran Docker on a VM. Milestone 5 moves container lifecycle management to GKE. We will
show healthy replicas, live replacement, real autoscaling, HTTPS, and health checks.
The original VM, private PostgreSQL database, upload bucket and secrets are preserved.”

Screen: HTTPS application and project title. Commands: none.
Expected: working UI without TLS warning. If unavailable, fix before recording.

## 1:00–2:00 Architecture (60 seconds)

Narration: “Our existing Autopilot cluster is scanner-gke in us-central1. One external
Application Load Balancer terminates HTTPS and routes through Ingress to Streamlit.
Streamlit makes server-side requests to the internal backend Service. Each Deployment
starts with two pods. The backend uses the existing SQL private IP and accesses GCS
and Secret Manager with the scanner-api workload identity. The frontend has no cloud
resource grants. HPA changes replica counts; PDB constrains voluntary evictions.”

Screen: finalized slide 1. Mention the actual hostname and certificate only after
verification. No terminal commands. If topology changes, update slide before filming.

## 2:00–3:00 Healthy replicas (60 seconds)

```powershell
gcloud.cmd container clusters list --project=file-security-scanner
kubectl get deployments -n scanner
kubectl get pods -n scanner -o wide
kubectl get services,ingress -n scanner
```

Narration: “These are live cluster results. We expect at least two available pods per
Deployment. ClusterIP keeps backend traffic inside Kubernetes; Ingress is our public
entry point.” Screen: cluster console and terminal. Read actual Ready/available counts.
If any pod is Pending/unready, inspect events and pause the demonstration until fixed.

## 3:00–4:30 Live replacement (90 seconds)

Terminal B before deletion:

```powershell
kubectl get pods -n scanner -w
```

Terminal A after explicit deletion approval:

```powershell
.\scripts\test-pod-recovery.ps1 -Approved
kubectl get deployments,pods -n scanner
```

Narration: “We delete exactly one Ready backend pod while at least two are healthy.
The ReplicaSet controller detects the shortfall and creates a new pod. Watch the new
name and UID become Ready. The PDB does not block direct pod deletion; the Deployment
controller is responsible for replacement.” Screen: live watch and before/after output.
Expected: new pod, Ready replacement and restored available count. Do not invent timing.
If slower than 90 seconds, investigate image pulls/scheduling; rehearse again before
the final continuous demonstration. Restart port-forward after deleting its target.

## 4:30–6:00 Autoscaling (90 seconds)

```powershell
kubectl get hpa,deployments -n scanner
kubectl top pods -n scanner
```

Terminal B:

```powershell
kubectl get hpa -n scanner -w
```

Terminal C, with port-forward already running:

```powershell
python scripts/test-autoscaling.py --seconds 180 --workers 64
```

Then:

```powershell
kubectl get hpa,deployments,pods -n scanner
```

Narration: “The backend HPA targets 60 percent of requested CPU, with minimum two and
maximum five replicas. This bounded traffic hits process health only: no scans, SQL
writes or paid Gemini calls. Watch measured CPU and desired/current replicas change.”
Read the actual counts. Additional pods must become Ready. Metrics and node provisioning
can exceed 90 seconds: rehearse first; if necessary start the visible load at 3:30 and
leave its terminal visible alongside pod recovery, then show current progress here.
Never present manual scaling as HPA. If health traffic fails to drive CPU, adjust
concurrency within the script's bounds or document an approved temporary CPU target
and restore it; collect the successful actual demonstration before filming.

## 6:00–7:00 HTTPS and redirect (60 seconds)

```powershell
kubectl get managedcertificate scanner-tls -n scanner
curl.exe -I https://scanner.136-69-114-222.sslip.io/
curl.exe -I http://scanner.136-69-114-222.sslip.io/
```

Narration: “The Google-managed certificate must show Active. The HTTPS request verifies
trust and hostname normally, without insecure flags. The HTTP response must redirect
to the same hostname over HTTPS.” Screen: certificate status, browser connection
details, then type HTTP URL and show HTTPS address. Read actual status and Location.
Provisioning/failed certificate or missing redirect means this segment is not ready.

## 7:00–8:00 Health strategy (60 seconds)

```powershell
Get-Content backend/health.py
Get-Content backend/database.py | Select-String -Pattern 'SELECT 1' -Context 5,2
kubectl describe deployment backend -n scanner
```

Narration: “Liveness /health/live checks responsiveness without database or external
calls. Readiness /health/ready executes SELECT 1 with connection and statement
timeouts. An unavailable database returns a generic 503, while liveness still returns
200. Kubernetes removes unready pods from ready Service endpoints rather than
restarting them just because SQL is unavailable.” Screen: slide 2, source and actual
probe settings. Show test log; do not disrupt the shared SQL instance.

## 8:00–9:00 PDB and GitHub (60 seconds)

```powershell
kubectl get pdb -n scanner
kubectl describe pdb backend -n scanner
git branch --show-current
git log -3 --oneline
```

Narration: “Each PDB requires one available replica during supported voluntary
evictions. Multiple replicas, readiness and rolling updates reduce interruptions;
PDBs do not guarantee zero downtime or prevent crashes or direct deletion. Our
milestone5-gke branch contains Deployments, Services, Ingress, managed certificate,
HPA, PDB, scripts and evidence.” Screen: actual GitHub branch/files after approved push.
If not pushed, state that explicitly; do not imply local commits are on GitHub.

## 9:00–10:00 Application and conclusion (60 seconds)

Screen: HTTPS UI. Upload harmless text, click Scan File, show actual risk and AI result,
then Load Scan History. Narration: “The UI calls our private backend. The uploaded
file is stored privately in the original bucket, and the new record joins historical
scans in PostgreSQL. GKE maintains desired replicas and scales from measured load.
HTTPS and readiness-aware routing complete the public deployment.”

If Gemini latency exceeds the slot, start the live scan earlier while explaining
health probes and return to its real result here. If AI fails, report the failure;
fix and retest rather than claiming success. End at about ten minutes.

## Submission checklist

- [ ] Every presenter has camera on for their portion; clear audio and readable terminal.
- [ ] Video shows live deletion/replacement and actual HPA replica increase.
- [ ] Exactly two final slides and half-page analysis reflect deployed settings.
- [ ] Upload completed team recording to OneDrive (not directly to Canvas).
- [ ] Grant view/edit access to sdesini@cougarnet.uh.edu, krajan@cougarnet.uh.edu,
      skolanu@cougarnet.uh.edu; verify intended access and link behavior.
- [ ] Submit the shareable OneDrive link in Canvas; verify submission receipt.
- [ ] Do not mark recording, sharing or Canvas complete without performing them.
