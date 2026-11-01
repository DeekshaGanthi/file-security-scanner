# Terraform ownership - November 1, 2026

User-approved adoption and infrastructure creation completed. Both remote states
report No changes with refresh enabled and detailed exit code 0.

| Resource | Terraform owner | Verified status / exception |
|---|---|---|
| Autopilot scanner-gke | root managed.tf | Imported; no cloud changes |
| Cloud SQL file-scanner-postgres | root managed.tf | Imported; private networking and database data preserved |
| Upload bucket | root managed.tf | Imported; private; force_destroy=false |
| Artifact Registry | root managed.tf | Imported |
| Two Secret Manager secrets | root managed.tf | Metadata imported; versions/payloads excluded |
| New CI identity/WIF/additive IAM | root iam.tf | Applied; repository/branch restricted |
| Metric/dashboard/alert/channel | root monitoring.tf | Applied; definitions verified |
| Private versioned state bucket | bootstrap/main.tf | Applied; separate remote prefix |
| Existing application IAM | External existing ownership | Existing grants preserved; not claimed as Terraform-managed |
| Default VPC/private services networking | Shared external ownership | Referenced by imported cluster/SQL; not imported to avoid conflicting shared ownership |
| Kubernetes resources | Git-managed manifests/release.py | Explicit exception; HPA owns replicas |
| HTTPS load balancer/certificate | GKE controller / Git Ingress | Explicit exception; avoid conflicting controller ownership |
| Billing budgets | External ownership | Read inspection HTTP 403; unchanged |
| SQL users/database schema | Existing application/migrations | Password values excluded from state/configuration |

Root backend bucket: file-security-scanner-tfstate-956088853573.
Root prefix: scanner/milestone6; bootstrap prefix: scanner/bootstrap.
State bucket has uniform access, public access prevention, versioning and
force_destroy=false. The deploy identity has no new state permissions.

The exact approved root plan was six imports, ten additions, zero updates/deletes.
Every imported resource has prevent_destroy; cluster/SQL retain deletion protection.
Autopilot node configuration/pools remain provider/GKE-managed. Two narrow lifecycle
exceptions preserve actual API state: empty Autopilot admission list (provider
otherwise introduces gke://*) and unset SQL maintenance day=0 (provider rejects
expressing zero). No blanket ignore_changes is used. Dashboard defaults are
explicitly represented rather than ignored.

The former adoption workspace is archived; executable imports/resources now live
only in terraform/imports.tf and terraform/managed.tf. No terraform destroy ran.
