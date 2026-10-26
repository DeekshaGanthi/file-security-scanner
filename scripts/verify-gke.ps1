param([Parameter(Mandatory=$true)][string]$Hostname)
$ErrorActionPreference = 'Stop'
$context = kubectl config current-context
if ($context -ne 'gke_file-security-scanner_us-central1_scanner-gke') { throw 'Wrong cluster context' }
$dir = Join-Path 'docs/milestone5-evidence' (Get-Date -Format 'yyyyMMdd-HHmmss')
New-Item -ItemType Directory -Force $dir | Out-Null
foreach ($resource in @('deployments','pods','services','endpointslices','ingress','hpa','pdb','managedcertificates')) {
    kubectl get $resource -n scanner -o wide 2>&1 | Tee-Object -FilePath "$dir/$resource.txt"
    if ($LASTEXITCODE) { throw "Failed: $resource" }
}
Get-Content scripts/pod-health.py | kubectl exec -i -n scanner deployment/backend -- python - | Tee-Object "$dir/database-health.txt"
if ($LASTEXITCODE) { throw 'Database or health check failed' }
curl.exe -sS --fail --max-time 30 -I "https://$Hostname/" | Tee-Object "$dir/https.txt"
if ($LASTEXITCODE) { throw 'HTTPS verification failed' }
$redirect = curl.exe -sS --max-time 30 -I "http://$Hostname/"
if ($LASTEXITCODE) { throw 'HTTP request failed' }
$redirect | Tee-Object "$dir/http-redirect.txt"
if (($redirect -join "`n") -notmatch 'HTTP/\S+ 30[1278]') { throw 'Missing HTTP redirect' }
if (($redirect -join "`n") -notmatch "Location: https://$([regex]::Escape($Hostname))(:443)?/") { throw 'Wrong redirect destination' }
Write-Output 'Review redirect Location, certificate Active, replica counts and HPA metrics. This script does not certify rubric completion.'
