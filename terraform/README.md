# Terraform operations

Infrastructure approved and applied November 1, 2026. Six existing resources are
imported in managed.tf/imports.tf; monitoring and keyless CI IAM are managed by
this root workspace. adoption/ is an archive, never a second state owner.
Kubernetes remains Git-managed and GKE owns controller-created load balancer objects.
See docs/milestone6/terraform-coverage.md for ownership exceptions.

Private versioned bucket: file-security-scanner-tfstate-956088853573.
Root prefix: scanner/milestone6. Bootstrap prefix: scanner/bootstrap.
Both states returned a refresh-enabled No changes plan with detailed exit 0.

PowerShell (Terraform on PATH, or use milestone6-tmp/tools/terraform.exe):

```powershell
$env:TF_VAR_notification_email = 'AUTHORIZED_TEAM_RECIPIENT'
terraform '-chdir=terraform' init '-backend-config=bucket=file-security-scanner-tfstate-956088853573' '-backend-config=prefix=scanner/milestone6'
terraform '-chdir=terraform' fmt -check -recursive
terraform '-chdir=terraform' validate
terraform '-chdir=terraform' plan -refresh=true -detailed-exitcode
$planExitCode = $LASTEXITCODE
Write-Host "Terraform plan exit code: $planExitCode"
```

Use ADC or a short-lived identity token. With gcloud user credentials, capture
gcloud.cmd auth print-access-token directly into GOOGLE_OAUTH_ACCESS_TOKEN without
printing it, then remove the environment variable afterward. Never put credentials
in configuration, logs, command arguments or Git. State and tfvars stay private.

Bootstrap checks use the same bucket, prefix=scanner/bootstrap, and
-chdir=terraform/bootstrap. Never share the application's prefix. The bootstrap
resource protects the state bucket from deletion. Never run Terraform destroy.
Review new cloud mutations before apply. Retained import blocks are idempotent;
do not rerun a historical candidate plan from the old adoption workspace.

Provider versions are locked. Two narrow imported-resource provider exceptions
are documented inline. Dashboard API column types and default axis are explicitly
represented; the dashboard definition is fully diffed rather than ignored.

References:
- https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/logging_metric
- https://docs.cloud.google.com/monitoring/alerts/manage-alerts-terraform
- https://docs.cloud.google.com/iam/docs/workload-identity-federation-with-deployment-pipelines
- https://docs.cloud.google.com/monitoring/api/v3/filters
