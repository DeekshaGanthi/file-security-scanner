# Cloud change proposal — approval required

Historical proposal: user approved on November 1, 2026, and all four operations
below are now complete. Both refreshed remote-state plans exit 0 with No changes.
The application deployment and controlled demonstrations remain separately gated.

1. Create only the dedicated private versioned state bucket defined in
   `terraform/bootstrap/main.tf`; prevent_destroy and force_destroy=false protect it.
   The bootstrap configuration validates; its real plan reports 1 addition, 0 changes, 0 destroys (exit 2). Keep bootstrap state private and migrate it to its own backend prefix after
   review. The application state uses a different prefix. Existing project IAM
   inheritance applies; do not give the deployment identity state access.
2. Adopt the six existing resources using `adoption/managed.tf` and imports, moved
   into the root workspace. Refreshed candidate plan: **6 imports, 0 additions,
   0 changes, 0 destroys**. Imports change Terraform ownership/state, not cloud
   settings. Recovery is a reviewed state backup/ownership correction, never
   cloud resource deletion.
3. Apply the root monitoring/CI identity configuration. Real isolated plan:
   **10 additions, 0 changes, 0 destroys**: one counter, dashboard, alert and
   authorized email channel; deploy service account, WIF pool/provider, impersonation
   member, registry writer member and cluster viewer member. No application identity
   grants are removed. WIF trust restricts repository and deployment branch.
4. Apply `k8s/cicd/rbac.yaml` as an administrator. Namespace Role/RoleBinding allow
   patching only the two Deployments and pod inspection/exec for health checks.
   Pod exec has application-level access: this is the material CI identity risk.

Risk: monitoring has modest ingestion/evaluation cost; alerts send email to the
authorized recipient. CI trust grants deployment and container-exec access to
code pushed on the deployment branch. State contains private configuration and
must remain restricted. Existing app replicas, SQL, uploads, secrets, HTTPS,
budgets and application IAM are preserved.

Rollback: restore prior monitoring definitions or disable only the new alert;
revoke the new WIF/CI bindings and namespace RoleBinding if needed. Preserve
imported infrastructure and state backups. Bucket destruction and Terraform destroy
are never part of this plan. A fresh full root plan must still be reviewed before
apply; changed or destructive actions invalidate this proposal.

Deployment promotion is a later review step: no commit/push to milestone6-deploy
is included here. That approval must identify tested commit SHA, expected immutable
images and the automated previous-template recovery path. The controlled 503
notification test and controlled failed rollout must also be explicitly scheduled
after normal deployment succeeds.
