# Milestone 6 baseline — November 1, 2026

Repository: https://github.com/DeekshaGanthi/file-security-scanner

Starting branch `milestone5-gke`, commit `ff5b478`; clean working tree. Local
development branch `milestone6-dev` created without changing Milestone 5 history.
No workflows or Terraform existed. Terraform was absent from PATH; checksum-verified
Terraform 1.14.9 was downloaded into ignored `milestone6-tmp/tools`.

## Verified live baseline

Project `file-security-scanner` (number `956088853573`), region `us-central1`.
Autopilot cluster `scanner-gke` RUNNING; workload and system logging enabled,
Kubernetes monitoring and managed Prometheus enabled. Workload identity pool:
`file-security-scanner.svc.id.goog`.

Namespace `scanner`: backend and frontend each 2/2 ready; all four pods Running,
zero restarts. Both HPAs have minimum 2, maximum 5; both PDBs minimum available 1.
Ingress address `136.69.114.222`; managed certificate `scanner-tls` Active.
https://scanner.136-69-114-222.sslip.io/ returned HTTP 200.

Cloud SQL instance `file-scanner-postgres`: PostgreSQL 18, `db-f1-micro`, private
network `default`, public IPv4 disabled, encrypted connections required,
backups and point-in-time recovery enabled. Database/user names remain represented
in existing manifests; no password payloads read during audit.

Upload bucket `file-security-scanner-uploads-2026`: US-CENTRAL1, uniform access,
public access prevention enforced. No existing state bucket returned by bucket list.
Docker repository `file-security-scanner-repo` in us-central1.
Secrets: `scanner-db-password`, `gemini-api-key` (metadata only).
VPC `default` is auto-mode; private services range `default-ip-range-1792183218032`;
reserved external address `scanner-gke-ip`. Existing application Kubernetes service
account is `scanner-api`; do not confuse it with a Google service account. The
Google service-account list returned only the default Compute Engine account.

No custom log-based metrics or Monitoring dashboards returned. Actual existing
backend logs use `k8s_container` with project, location, cluster, namespace and
container labels matching the intended metric scope. Those sampled entries were
unstructured. Existing health routes: `/health/live`, `/health/ready` (database).
Baseline tests: 6 passed.

## Architecture and ownership

HTTPS Google load balancer → Streamlit frontend → internal FastAPI backend →
YARA/Gemini, private PostgreSQL, private GCS. Secret Manager supplies credentials.
Git-managed Kubernetes manifests already define probes, rolling updates,
non-root execution, read-only root filesystems, HPA, PDB, Ingress and certificate.

## Risks and plan

1. Preserve all Milestone 5 resources and security controls.
2. Add allowlisted JSON request logs and a separate loopback-only error listener.
3. Validate the numeric 5xx filter against deployed JSON before monitoring apply.
4. Review generated Terraform resource configuration and secure state ownership;
   import existing resources without recreating them.
5. Review additive WIF/IAM and namespace RBAC before activation.
6. Promote tested code to `milestone6-deploy` only after deployment approval.
7. Verify successful rollout, controlled readiness failure, recovery, metric data,
   received notification, and screenshots. Configuration alone is not evidence.

Live changes, Terraform apply/import/state initialization, and deployment-branch
promotion remain gated by the explicit review requirements in the supplied prompt.
Budget API inspection returned HTTP 403; billing is enabled but budgets could not be verified. A read-only SQL SELECT 1 succeeded.
