# Read-only checks, except the explicitly marked controlled-error demonstration.
# Run from repository root. Never print credentials or Terraform state.
$ErrorActionPreference = 'Stop'

kubectl get deployments,pods,hpa,pdb,ingress,managedcertificate -n scanner
curl.exe -I https://scanner.136-69-114-222.sslip.io/

# Real JSON request logs; use a UUID from evidence/logging/controlled-requests.json.
$filter = 'resource.type="k8s_container" AND resource.labels.cluster_name="scanner-gke" AND resource.labels.namespace_name="scanner" AND jsonPayload.event="http_request"'
gcloud.cmd logging read $filter --project=file-security-scanner --freshness=30m --limit=10 --format=json
gcloud.cmd logging metrics describe scanner_http_5xx_count --project=file-security-scanner
gcloud.cmd monitoring dashboards list --project=file-security-scanner

# Re-check the recorded real 200/404/503 log correlation and metric evidence:
python scripts/milestone6-verify-observability.py

# OPTIONAL controlled error: sends one 503 and can send an alert notification.
# Run only when intentionally repeating the authorized demonstration:
# python scripts/milestone6-controlled-probe.py

# Monitoring policy and actual alert incident, without displaying recipient labels:
$monitorToken = gcloud.cmd auth print-access-token
if ($LASTEXITCODE) { throw 'Cloud authentication failed' }
try {
    $headers = @{ Authorization = "Bearer $monitorToken"; 'x-goog-user-project' = 'file-security-scanner' }
    $policy = Invoke-RestMethod -Headers $headers -Uri 'https://monitoring.googleapis.com/v3/projects/file-security-scanner/alertPolicies/3124806542354479175'
    $policy | Select-Object name, displayName, enabled, conditions
    Invoke-RestMethod -Headers $headers -Uri 'https://monitoring.googleapis.com/v3/projects/file-security-scanner/alerts/0.oeimw7fsr668'
} finally {
    $monitorToken = $null
    $headers = $null
}

# With GitHub CLI installed and authenticated:
# gh run list --repo DeekshaGanthi/file-security-scanner --branch milestone6-deploy
# gh run view 41358659674 --repo DeekshaGanthi/file-security-scanner
# gh run view 41359525217 --repo DeekshaGanthi/file-security-scanner

# Terraform: supply the authorized recipient privately via TF_VAR_notification_email.
# Use ADC or a short-lived GOOGLE_OAUTH_ACCESS_TOKEN, never print it.
# terraform '-chdir=terraform' init '-backend-config=bucket=file-security-scanner-tfstate-956088853573' '-backend-config=prefix=scanner/milestone6'
# terraform '-chdir=terraform' validate
# terraform '-chdir=terraform' plan -refresh=true -detailed-exitcode
# $planExitCode = $LASTEXITCODE
# Write-Host "Terraform plan exit code: $planExitCode"
