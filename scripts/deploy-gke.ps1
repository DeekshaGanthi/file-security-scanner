param([Parameter(Mandatory=$true)][string]$ManifestDirectory)
$ErrorActionPreference = 'Stop'
foreach ($tool in @('gcloud.cmd','kubectl','python')) { Get-Command $tool -ErrorAction Stop | Out-Null }
if ((gcloud.cmd config get-value project) -ne 'file-security-scanner') { throw 'Wrong active project' }
if (-not (gcloud.cmd auth list --filter=status:ACTIVE --format='value(account)')) { throw 'Not authenticated' }
gcloud.cmd container clusters describe scanner-gke --region=us-central1 --project=file-security-scanner --format='value(status)'
if ($LASTEXITCODE) { throw 'Cluster unavailable' }
gcloud.cmd container clusters get-credentials scanner-gke --region=us-central1 --project=file-security-scanner
if ($LASTEXITCODE) { throw 'Credentials unavailable' }
$files = Get-ChildItem -LiteralPath $ManifestDirectory -Filter '*.yaml'
if ($files.Count -lt 15) { throw 'Use the complete rendered directory' }
if (Select-String -Path $files.FullName -Pattern 'BUILD_REQUIRED') { throw 'Unbuilt image' }
kubectl apply --dry-run=client -f $ManifestDirectory
if ($LASTEXITCODE) { throw 'Client validation failed' }
kubectl apply -f (Join-Path $ManifestDirectory 'namespace.yaml')
if ($LASTEXITCODE) { throw 'Namespace failed' }
kubectl get secret streamlit-session -n scanner -o name 2>$null | Out-Null
if ($LASTEXITCODE) {
    python scripts/ensure-session-secret.py | kubectl create -f -
    if ($LASTEXITCODE) { throw 'Session secret creation failed' }
}
kubectl apply --dry-run=server -f $ManifestDirectory
if ($LASTEXITCODE) { throw 'Server validation failed' }
kubectl apply -f $ManifestDirectory
if ($LASTEXITCODE) { throw 'Apply failed' }
foreach ($component in @('backend','frontend')) {
    kubectl rollout status deployment/$component -n scanner --timeout=900s
    if ($LASTEXITCODE) { throw "Rollout failed: $component" }
}
kubectl get deployments,pods,services,ingress,hpa,pdb -n scanner
