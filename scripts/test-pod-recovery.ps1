param([switch]$Approved)
$ErrorActionPreference = 'Stop'
if (-not $Approved) { throw 'Obtain explicit approval for deleting one pod, then pass -Approved' }
if ((kubectl config current-context) -ne 'gke_file-security-scanner_us-central1_scanner-gke') { throw 'Wrong cluster' }
$pods = kubectl get pods -n scanner -l app=backend -o json | ConvertFrom-Json
if ($LASTEXITCODE) { throw 'Cannot read pods' }
$ready = @($pods.items | Where-Object { -not $_.metadata.deletionTimestamp -and ($_.status.conditions | Where-Object { $_.type -eq 'Ready' -and $_.status -eq 'True' }) })
if ($ready.Count -lt 2) { throw 'Need two Ready backend pods' }
$dir = Join-Path 'docs/milestone5-evidence' ('recovery-'+(Get-Date -Format 'yyyyMMdd-HHmmss'))
New-Item -ItemType Directory -Force $dir | Out-Null
kubectl get pods -n scanner -o wide | Tee-Object "$dir/before.txt"
$target = $ready[0].metadata.name
"Deleting exactly one pod: $target" | Tee-Object "$dir/deletion.txt"
kubectl delete pod $target -n scanner --wait=false | Tee-Object -Append "$dir/deletion.txt"
if ($LASTEXITCODE) { throw 'Delete failed' }
$deadline = (Get-Date).AddMinutes(10)
do {
    $current = kubectl get pods -n scanner -l app=backend -o json | ConvertFrom-Json
    $replacement = @($current.items | Where-Object { $_.metadata.uid -notin $pods.items.metadata.uid -and ($_.status.conditions | Where-Object { $_.type -eq 'Ready' -and $_.status -eq 'True' }) })
    if ($replacement.Count) { break }
    Start-Sleep -Seconds 3
} while ((Get-Date) -lt $deadline)
if (-not $replacement.Count) { throw 'Replacement readiness not observed' }
kubectl get pods -n scanner -o wide | Tee-Object "$dir/after.txt"
Write-Output "Observed Ready replacement: $($replacement[0].metadata.name)"
