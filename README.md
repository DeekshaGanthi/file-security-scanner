# AI File Security Scanner

Python FastAPI and Streamlit static file analysis, with risk scoring, YARA,
optional VirusTotal lookup, Gemini explanation, PostgreSQL history and private GCS uploads.

## Milestone 5 GKE deployment

Application: https://scanner.136-69-114-222.sslip.io/

Cluster `scanner-gke`, region `us-central1`, namespace `scanner`.
Two minimum replicas each for frontend/backend, HPA 2-5 at 60% requested CPU,
PDB minAvailable 1, private SQL and workload identity. GCE Ingress terminates
Google-managed HTTPS and redirects HTTP. The original VM remains operational.

Read [deployment instructions](docs/MILESTONE5_DEPLOYMENT.md),
[architecture and costs](docs/MILESTONE5_ARCHITECTURE.md),
[verification](docs/MILESTONE5_VERIFICATION.md), and
[rubric status](docs/MILESTONE5_RUBRIC.md).
AI generation is subject to external API quota; observed rate limiting is documented.

## Local development

Use Python 3.12 and install `requirements.txt`, plus `requirements-dev.txt` for tests.
Provide DB_HOST, DB_NAME, DB_USER and DB_PASSWORD (or DB_PASSWORD_SECRET) securely.
GCS_BUCKET_NAME is required. GEMINI_API_KEY or GEMINI_API_KEY_SECRET enables AI.
ADC is used for cloud access. Never commit `.env`, tokens or service account keys.

```powershell
python -m pytest -q
uvicorn backend.main:app --host 0.0.0.0 --port 8000
# Separate terminal:
streamlit run frontend/app.py
```

`GET /health/live` is process-only. `GET /health/ready` checks PostgreSQL with SELECT 1.
Schema management is separate; application startup does not rerun migrations.
The existing Dockerfile and Compose configuration remain available for Milestone 4.
